"""
FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Then check:
    http://localhost:8000/health
    http://localhost:8000/docs   (Swagger UI)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth
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

# Document router will be included here once upload endpoints are built:
# from app.api.routes import documents
# app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
