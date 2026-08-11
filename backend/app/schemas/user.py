import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Public self-registration: always creates a new Company with this
    user as its Admin."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    company_name: str = Field(min_length=1, max_length=255)


class StaffCreate(BaseModel):
    """Used by an Admin to create a Staff account inside their own company."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    company_id: uuid.UUID | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)