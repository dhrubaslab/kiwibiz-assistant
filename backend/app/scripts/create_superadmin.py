"""
One-off CLI script to create the platform's Super Admin account.
Not exposed via the API — SaaS-provider-level access shouldn't be self-serve.

Usage:
    cd backend
    source venv/bin/activate
    python -m app.scripts.create_superadmin
"""

import getpass

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User, UserRole


def main():
    email = input("Super Admin email: ").strip()
    password = getpass.getpass("Super Admin password: ")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"A user with email {email} already exists.")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            company_id=None,
        )
        db.add(user)
        db.commit()
        print(f"Super Admin created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()