import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    content_type: str | None
    file_size_bytes: int | None
    status: DocumentStatus
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDownloadResponse(BaseModel):
    download_url: str
    expires_in_seconds: int
