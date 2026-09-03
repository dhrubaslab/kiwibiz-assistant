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
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.conversation import Conversation, Message, MessageRole
from app.models.user import User
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    ConversationDetail,
    ConversationSummary,
    MessageSchema,
    SourceSchema,
)

from app.services.embeddings import embed_query
from app.services.rag_qa import generate_answer
from app.services.retrieval import retrieve_relevant_chunks

router = APIRouter()

PREVIEW_MAX_LENGTH = 80


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


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
 
    summaries = []
    for conv in conversations:
        first_user_message = next(
            (m for m in conv.messages if m.role == MessageRole.USER), None
        )
        preview = first_user_message.content if first_user_message else "(empty conversation)"
        if len(preview) > PREVIEW_MAX_LENGTH:
            preview = preview[:PREVIEW_MAX_LENGTH].rstrip() + "…"
 
        summaries.append(
            ConversationSummary(id=conv.id, preview=preview, created_at=conv.created_at)
        )
    return summaries



@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
 
    messages = [
        MessageSchema(
            id=m.id,
            role=m.role.value,
            text=m.content,
            sources=[SourceSchema(**s) for s in m.sources] if m.sources else None,
            timestamp=m.created_at,
        )
        for m in conversation.messages
    ]
    return ConversationDetail(id=conversation.id, messages=messages)


def _build_history(conversation: Conversation, db: Session, exclude_message_id) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id, Message.id != exclude_message_id)
        .order_by(Message.created_at)
        .all()
    )
    return [{"role": m.role.value, "content": m.content} for m in messages]
