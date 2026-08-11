from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import RequireRole, get_db
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate, SubscriptionUpdate

router = APIRouter()


# --- Admin: manage their own company's profile ---

@router.get("/me", response_model=CompanyResponse)
def read_my_company(
    current_user: User = Depends(RequireRole(UserRole.ADMIN, UserRole.STAFF)),
):
    return current_user.company


@router.patch("/me", response_model=CompanyResponse)
def update_my_company(
    payload: CompanyUpdate,
    current_user: User = Depends(RequireRole(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    company = current_user.company
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


# --- Super Admin: manage every company ---

@router.get("", response_model=list[CompanyResponse])
def list_companies(
    current_user: User = Depends(RequireRole(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
):
    return db.query(Company).order_by(Company.created_at.desc()).all()


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    current_user: User = Depends(RequireRole(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
):
    """Creates a bare company profile with no user attached — an Admin
    account gets linked to it separately later."""
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
def read_company(
    company_id: str,
    current_user: User = Depends(RequireRole(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found.")
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    payload: CompanyUpdate,
    current_user: User = Depends(RequireRole(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company

@router.patch("/{company_id}/subscription", response_model=CompanyResponse)
def update_subscription(
    company_id: str,
    payload: SubscriptionUpdate,
    current_user: User = Depends(RequireRole(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found.")

    company.is_active = payload.is_active
    company.subscription_type = payload.subscription_type
    company.subscription_expires_at = payload.subscription_expires_at
    db.commit()
    db.refresh(company)
    return company