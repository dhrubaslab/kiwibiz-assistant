"""
Embedding service — wraps OpenAI's embeddings endpoint. Batches requests
(the API accepts a list of inputs per call) to avoid one HTTP round-trip
per chunk, which matters once a document produces dozens of chunks.

Requires OPENAI_API_KEY to be set in your environment/config (already
configured per project notes).
"""

from openai import OpenAI

from app.config import settings  # adjust import if your settings object lives elsewhere

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per call; 100 keeps payloads modest

_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds a list of strings, returning one embedding vector per input,
    in the same order. Batches internally.
    """
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = _client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        # response.data is already ordered to match the input batch order
        all_embeddings.extend([item.embedding for item in response.data])

    return all_embeddings


def embed_query(text: str) -> list[float]:
    """Embeds a single query string (e.g. the user's question)."""
    return embed_texts([text])[0]
