import uuid

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    conversation_id: uuid.UUID | None = None


class SourceSchema(BaseModel):
    document_id: uuid.UUID
    document_name: str
    chunk_text: str
    page_number: int | None
    score: float


class AskResponse(BaseModel):
    answer: str
    conversation_id: uuid.UUID
    sources: list[SourceSchema]
