"""
Company model — represents a subscribing SME organisation. An Admin heads
the company; Staff belong to it. The Super Admin (SaaS provider) controls
`is_active`, `subscription_type`, and `subscription_expires_at` — disabling
a company cascades to every Admin/Staff user under it (enforced in
app.api.deps.get_current_user), without touching individual user rows.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubscriptionType(str, enum.Enum):
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    ELITE_YEARLY = "elite_yearly"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Subscription — set by the Super Admin only.
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        SAEnum(SubscriptionType, name="subscription_type", native_enum=True),
        default=SubscriptionType.FREE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="company")

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"