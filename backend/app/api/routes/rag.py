"""
RAG Q&A endpoint. Flow per request:

1. Resolve or create the Conversation (scoped to the current user).
2. Embed the question.
3. Retrieve the top-K most similar document_chunks for the user's company.
4. Pull recent conversation history for multi-turn context.
5. Call OpenAI to generate a grounded answer.
6. Persist both the user's question and the assistant's answer as Messages.
7. Return the shape the frontend's chat store already expects.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.conversation import Conversation, Message, MessageRole
from app.models.user import User
from app.schemas.rag import AskRequest, AskResponse, SourceSchema
from app.services.embeddings import embed_query
from app.services.rag_qa import generate_answer
from app.services.retrieval import retrieve_relevant_chunks

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    conversation = _get_or_create_conversation(payload.conversation_id, current_user, db)

    # Persist the user's message first, so it's saved even if generation fails downstream.
    user_message = Message(conversation_id=conversation.id, role=MessageRole.USER, content=question)
    db.add(user_message)
    db.commit()

    # Retrieve
    query_embedding = embed_query(question)
    retrieved = retrieve_relevant_chunks(db, current_user.company_id, query_embedding)

    # Build history (exclude the message we just added, since it's passed separately)
    history = _build_history(conversation, db, exclude_message_id=user_message.id)

    # Generate
    answer_text = generate_answer(question, retrieved, history)

    sources_payload = [
        {
            "document_id": str(chunk.document_id),
            "document_name": chunk.document_name,
            "chunk_text": chunk.chunk_text,
            "page_number": chunk.page_number,
            "score": chunk.score,
        }
        for chunk in retrieved
    ]

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=answer_text,
        sources=sources_payload,
    )
    db.add(assistant_message)
    db.commit()

    return AskResponse(
        answer=answer_text,
        conversation_id=conversation.id,
        sources=[SourceSchema(**s) for s in sources_payload],
    )


def _get_or_create_conversation(
    conversation_id, current_user: User, db: Session
) -> Conversation:
    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
        return conversation

    conversation = Conversation(user_id=current_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def _build_history(conversation: Conversation, db: Session, exclude_message_id) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id, Message.id != exclude_message_id)
        .order_by(Message.created_at)
        .all()
    )
    return [{"role": m.role.value, "content": m.content} for m in messages]
