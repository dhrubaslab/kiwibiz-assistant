import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.company import SubscriptionType


class CompanyCreate(BaseModel):
    """Used by Super Admin to create a bare company profile — no user attached yet."""
    name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    phone: str | None = None
    industry: str | None = None
    address: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    contact_email: EmailStr | None = None
    industry: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    contact_email: str | None
    industry: str | None
    phone: str | None
    address: str | None
    website: str | None
    subscription_type: SubscriptionType
    is_active: bool
    subscription_expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionUpdate(BaseModel):
    is_active: bool
    subscription_type: SubscriptionType
    subscription_expires_at: datetime | None = None