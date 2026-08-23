"""
RAG ingestion pipeline — orchestrates extraction, chunking, embedding,
and storage for a single Document. Designed to run as a FastAPI
BackgroundTask right after upload, so the upload response returns
immediately while processing happens after.

Document.status transitions: UPLOADED -> PROCESSING -> PROCESSED | FAILED.
"""

import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services import storage
from app.services.chunking import chunk_segments
from app.services.embeddings import embed_texts
from app.services.text_extraction import UnsupportedContentTypeError, extract_text

logger = logging.getLogger(__name__)


def process_document(document_id) -> None:
    """
    Entry point for the background task. Opens its own DB session since
    it runs outside the request's session lifecycle.
    """
    db: Session = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error("process_document: document %s not found", document_id)
            return

        document.status = DocumentStatus.PROCESSING
        db.commit()

        try:
            _run_pipeline(document, db)
            document.status = DocumentStatus.PROCESSED
            db.commit()
        except UnsupportedContentTypeError as exc:
            logger.warning("Document %s: %s", document_id, exc)
            document.status = DocumentStatus.FAILED
            db.commit()
        except Exception:
            logger.exception("Document %s: processing failed", document_id)
            document.status = DocumentStatus.FAILED
            db.commit()

    finally:
        db.close()


def _run_pipeline(document: Document, db: Session) -> None:
    # 1. Fetch the raw file bytes from storage (local or S3, per your
    #    storage abstraction — adjust method name if it differs).
    file_bytes = storage.download_file(document.s3_key)

    # 2. Extract text (page-aware for PDFs)
    segments = extract_text(document, file_bytes)
    if not segments:
        logger.warning("Document %s: no extractable text found", document.id)
        return

    # 3. Chunk
    chunks = chunk_segments(segments)
    if not chunks:
        return

    # 4. Embed (batched)
    embeddings = embed_texts([c.text for c in chunks])

    # 5. Clear any existing chunks for this document (handles reprocessing)
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    # 6. Store
    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk.text,
                page_number=chunk.page_number,
                embedding=embedding,
            )
        )

    db.commit()
    logger.info("Document %s: stored %d chunks", document.id, len(chunks))
