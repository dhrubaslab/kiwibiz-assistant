"""
Admin stats dashboard endpoint: document counts by category, upload
activity over the last 30 days, and Q&A usage over the last 30 days.

Admin-only — Staff don't get visibility into company-wide usage stats.
Scoped to the current user's company via the same User.company_id join
pattern used in documents.py (Document/Conversation have no company_id
column directly; company is reached through the owning User).
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import cast, func
from sqlalchemy.types import Date
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.conversation import Conversation, Message, MessageRole
from app.models.document import Document
from app.models.user import User, UserRole
from app.schemas.stats import CategoryCount, DailyCount, StatsDashboardResponse

router = APIRouter()

ACTIVITY_WINDOW_DAYS = 30


def _require_admin(current_user: User) -> None:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can view usage stats.",
        )


@router.get("/dashboard", response_model=StatsDashboardResponse)
def get_stats_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)

    since = date.today() - timedelta(days=ACTIVITY_WINDOW_DAYS)

    # Documents by category — all-time, company-scoped
    category_rows = (
        db.query(Document.category, func.count(Document.id))
        .join(User, Document.owner_id == User.id)
        .filter(User.company_id == current_user.company_id)
        .group_by(Document.category)
        .all()
    )
    by_category = [
        CategoryCount(category=category.value, count=count) for category, count in category_rows
    ]

    # Upload activity — last 30 days, company-scoped
    upload_rows = (
        db.query(cast(Document.uploaded_at, Date).label("day"), func.count(Document.id))
        .join(User, Document.owner_id == User.id)
        .filter(User.company_id == current_user.company_id)
        .filter(Document.uploaded_at >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    upload_activity = [DailyCount(date=day, count=count) for day, count in upload_rows]

    # Q&A usage — count of user-asked questions per day, last 30 days,
    # company-scoped via Conversation.user_id -> User.company_id
    qa_rows = (
        db.query(cast(Message.created_at, Date).label("day"), func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .join(User, Conversation.user_id == User.id)
        .filter(User.company_id == current_user.company_id)
        .filter(Message.role == MessageRole.USER)
        .filter(Message.created_at >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    qa_usage = [DailyCount(date=day, count=count) for day, count in qa_rows]

    return StatsDashboardResponse(
        by_category=by_category,
        upload_activity=upload_activity,
        qa_usage=qa_usage,
    )