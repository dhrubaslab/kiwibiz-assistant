"""
FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Then check:
    http://localhost:8000/health
    http://localhost:8000/docs   (Swagger UI)
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import auth, companies, documents, users, rag
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check():
    """Basic liveness check — confirms the app is up and settings loaded."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
# Serves locally-stored documents when STORAGE_BACKEND = "local" (see
# app/config.py). If STORAGE_BACKEND = "s3", this directory simply stays
# empty/unused and download links come from S3's presigned URLs instead.
Path(settings.LOCAL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_DIR), name="uploads")
