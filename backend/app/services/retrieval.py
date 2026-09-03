"""
Retrieval — given a query embedding, finds the most similar document
chunks belonging to the current user's company. Company scoping mirrors
the same join pattern documents.py already uses for list_documents:
document_chunks -> documents -> users -> filter by company_id.
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User

TOP_K = 5


@dataclass
class RetrievedChunk:
    document_id: UUID
    document_name: str
    chunk_text: str
    page_number: int | None
    score: float  # similarity score, 0-1 (higher = more similar)


def retrieve_relevant_chunks(
    db: Session, company_id: UUID, query_embedding: list[float], top_k: int = TOP_K
) -> list[RetrievedChunk]:
    """
    Returns the top_k most similar chunks to query_embedding, restricted to
    documents owned by any user in company_id. Uses pgvector's cosine_distance
    comparator, ordering by ascending distance (= descending similarity).
    """
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    rows = (
        db.query(DocumentChunk, Document.original_filename, distance.label("distance"))
        .join(Document, DocumentChunk.document_id == Document.id)
        .join(User, Document.owner_id == User.id)
        .filter(User.company_id == company_id)
        .order_by(distance.asc())
        .limit(top_k)
        .all()
    )

    results: list[RetrievedChunk] = []
    for chunk, filename, dist in rows:
        # cosine_distance returns 0 (identical) to 2 (opposite); convert to a
        # 0-1 similarity score that's intuitive for the frontend's badge.
        similarity = max(0.0, 1.0 - (dist / 2.0))
        results.append(
            RetrievedChunk(
                document_id=chunk.document_id,
                document_name=filename,
                chunk_text=chunk.content,
                page_number=chunk.page_number,
                score=round(similarity, 4),
            )
        )
    return results
