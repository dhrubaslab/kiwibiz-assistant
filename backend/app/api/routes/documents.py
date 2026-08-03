"""
Document endpoints: upload, list, get a download link, and delete.

Every endpoint here requires auth (get_current_user) and every query is
scoped to `owner_id == current_user.id` — one user can never see or touch
another user's documents.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentDownloadResponse, DocumentResponse
from app.services import storage

router = APIRouter()

# Keep this list narrow and explicit — it's the first line of defence
# against unexpected file types landing in the RAG pipeline later.
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{file.content_type}' is not supported. "
            f"Allowed types: PDF, TXT, CSV, DOCX, XLSX.",
        )

    # Read into memory to check size; fine for a 20MB ceiling. If limits grow
    # much larger later, switch to streaming size checks instead.
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 20MB size limit.",
        )
    await file.seek(0)

    object_key = storage.build_object_key(current_user.id, file.filename)
    storage.upload_file(file.file, object_key, content_type=file.content_type)

    document = Document(
        owner_id=current_user.id,
        original_filename=file.filename,
        s3_key=object_key,
        content_type=file.content_type,
        file_size_bytes=len(contents),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


def _get_owned_document_or_404(document_id: uuid.UUID, current_user: User, db: Session) -> Document:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}/download", response_model=DocumentDownloadResponse)
def get_download_link(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _get_owned_document_or_404(document_id, current_user, db)
    expires_in = 3600
    url = storage.get_download_url(document.s3_key, expires_in=expires_in)
    return DocumentDownloadResponse(download_url=url, expires_in_seconds=expires_in)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _get_owned_document_or_404(document_id, current_user, db)
    storage.delete_file(document.s3_key)
    db.delete(document)
    db.commit()
    return None
