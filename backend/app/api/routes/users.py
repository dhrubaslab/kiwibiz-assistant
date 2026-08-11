from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import RequireRole, get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import StaffCreate, UserResponse, UserStatusUpdate

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def list_company_users(
    current_user: User = Depends(RequireRole(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return db.query(User).filter(User.company_id == current_user.company_id).all()


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    payload: StaffCreate,
    current_user: User = Depends(RequireRole(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    staff = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.STAFF,
        company_id=current_user.company_id,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_staff_status(
    user_id: str,
    payload: UserStatusUpdate,
    current_user: User = Depends(RequireRole(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    target = (
        db.query(User)
        .filter(User.id == user_id, User.company_id == current_user.company_id)
        .first()
    )
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found in your company.")
    if target.id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot change your own status.")

    target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return target