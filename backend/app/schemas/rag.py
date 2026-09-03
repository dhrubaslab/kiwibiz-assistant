import uuid
from datetime import datetime
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

class ConversationSummary(BaseModel):
    id: uuid.UUID
    preview: str
    created_at: datetime
 
 
class MessageSchema(BaseModel):
    id: uuid.UUID
    role: str
    text: str
    sources: list[SourceSchema] | None = None
    timestamp: datetime
 
 
class ConversationDetail(BaseModel):
    id: uuid.UUID
    messages: list[MessageSchema]