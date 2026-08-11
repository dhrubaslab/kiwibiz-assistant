"""
Shared FastAPI dependencies: DB session, current-user resolution (with
company-subscription cascade), and role-based access control.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import SessionLocal
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # Cascade: a disabled company blocks every Admin/Staff under it,
    # regardless of their individual is_active flag. Super Admin has no
    # company and is exempt from this check.
    if user.role != UserRole.SUPER_ADMIN:
        if user.company is None or not user.company.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your company's access has been disabled. Contact your administrator.",
            )

    return user


class RequireRole:
    """Dependency factory restricting an endpoint to specific roles.

    Usage:
        current_user: User = Depends(RequireRole(UserRole.ADMIN))
        current_user: User = Depends(RequireRole(UserRole.ADMIN, UserRole.STAFF))
    """

    def __init__(self, *allowed_roles: UserRole):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user