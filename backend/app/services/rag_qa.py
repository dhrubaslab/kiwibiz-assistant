"""
Answer generation — builds a grounded prompt from retrieved chunks plus
recent conversation history, then calls OpenAI's chat completion endpoint.

Kept as a plain OpenAI chat call rather than a full LangChain chain for
now: for a single-hop retrieve-then-answer flow, LangChain's abstraction
doesn't buy much over a direct call, and a direct call is easier to
debug/reason about. If multi-step retrieval (query rewriting, re-ranking,
tool use) gets added later, revisit and introduce LangChain's
ConversationalRetrievalChain at that point.
"""

from openai import OpenAI

from app.config import settings
from app.services.retrieval import RetrievedChunk

CHAT_MODEL = "gpt-4o-mini"
MAX_HISTORY_TURNS = 6  # last N messages (user+assistant combined) for context

# SYSTEM_PROMPT = """You are Kiwi-Biz Assistant, a document Q&A helper for a New Zealand \
# small business. Answer the user's question using ONLY the document excerpts provided \
# below. If the excerpts don't contain enough information to answer, say so clearly \
# rather than guessing or using outside knowledge. Be concise and direct. When relevant, \
# mention which document(s) your answer draws from."""

SYSTEM_PROMPT = """You are Kiwi-Biz Assistant, a document Q&A helper for a New Zealand \
small business. Answer the user's question using ONLY the document excerpts provided \
below. If the excerpts don't contain enough information to answer, say so clearly \
rather than guessing or using outside knowledge. Be concise and direct.

The excerpts are labeled [1], [2], [3] etc. purely so you can tell them apart internally. \
NEVER include these bracket numbers, or phrases like "document [2]" or "excerpt 3", in \
your answer — the user already sees a separate source list with real document names, so \
repeating numbered references is redundant and confusing. If you want to mention a source \
by name, use its actual filename (e.g. "the Refund Policy document") instead of a number."""

_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_answer(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    history: list[dict],  # [{role: "user"|"assistant", content: str}, ...]
) -> str:
    context_block = _build_context_block(retrieved_chunks)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY_TURNS:])
    messages.append(
        {
            "role": "user",
            "content": f"Document excerpts:\n{context_block}\n\nQuestion: {question}",
        }
    )

    response = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "(No relevant documents found.)"

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        page_info = f", page {chunk.page_number}" if chunk.page_number else ""
        parts.append(f"[{i}] {chunk.document_name}{page_info}:\n{chunk.chunk_text}")
    return "\n\n".join(parts)
