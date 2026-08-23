"""
Storage dispatcher — the single place documents.py talks to for file
storage. Routes to either app.services.s3 or app.services.local_storage
based on settings.STORAGE_BACKEND, so the rest of the app never needs an
if/else on which backend is active.

To switch backends: change STORAGE_BACKEND in app/config.py (or set it via
the STORAGE_BACKEND env var / .env) between "local" and "s3". Nothing else
needs to change.
"""

import uuid
from typing import BinaryIO

from app.config import settings
from app.services import local_storage, s3


def build_object_key(user_id: uuid.UUID, filename: str) -> str:
    """Shared key naming for both backends: users/<user_id>/<uuid>_<filename>"""
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    return f"users/{user_id}/{uuid.uuid4()}_{safe_filename}"


def upload_file(file_obj: BinaryIO, key: str, content_type: str | None = None) -> None:
    if settings.STORAGE_BACKEND == "s3":
        s3.upload_fileobj(file_obj, key, content_type=content_type)
    else:
        local_storage.save_file(file_obj, key, content_type=content_type)


def delete_file(key: str) -> None:
    if settings.STORAGE_BACKEND == "s3":
        s3.delete_object(key)
    else:
        local_storage.delete_file(key)


def get_download_url(key: str, expires_in: int = 3600) -> str:
    """
    S3: a temporary presigned URL.
    Local: a relative path served by the /uploads static mount in main.py
    (works fine for local dev; not meant for production use as-is).
    """
    if settings.STORAGE_BACKEND == "s3":
        return s3.generate_presigned_download_url(key, expires_in=expires_in)
    return f"/uploads/{key}"

def download_file(key: str) -> bytes:
    """
    Returns the raw bytes of a stored file, regardless of backend.
    Used by the RAG ingestion pipeline to read a document's content
    for text extraction.
    """
    if settings.STORAGE_BACKEND == "s3":
        return s3.download_fileobj(key)
    return local_storage.file_path_for_key(key).read_bytes()