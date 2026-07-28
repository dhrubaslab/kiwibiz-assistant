"""
Shared FastAPI dependencies.

`get_db` gives endpoints a request-scoped DB session.
`get_current_user` will be filled in once the User model + login endpoint
exist — for now it decodes the JWT and returns the subject (user id),
raising 401 if the token is missing/invalid. Swap the return value for a
real User lookup once app/models/user.py exists.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import SessionLocal

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
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    # TODO (auth endpoints step): look up the User row by user_id via `db`
    # and return the model instance instead of the raw id.
    return user_id
