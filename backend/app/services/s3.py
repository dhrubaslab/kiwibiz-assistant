"""
Thin wrapper around boto3 for the document-storage operations we need:
upload, delete, and a presigned URL for temporary download access.

Credentials come from app.config.settings (which reads AWS_ACCESS_KEY_ID /
AWS_SECRET_ACCESS_KEY from .env). If those are left blank, boto3 falls back
to its default credential chain (e.g. `aws configure` profile, env vars),
so either approach works.
"""

import uuid
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.config import settings

_s3_client = None


def get_s3_client():
    """Lazily create a single boto3 S3 client, reused across requests."""
    global _s3_client
    if _s3_client is None:
        kwargs = {"region_name": settings.AWS_REGION}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        _s3_client = boto3.client("s3", **kwargs)
    return _s3_client


def build_object_key(user_id: uuid.UUID, filename: str) -> str:
    """
    Namespaced, collision-proof S3 key: users/<user_id>/<uuid>_<original_filename>
    Keeping the original filename in the key (rather than only in the DB)
    makes objects easier to identify when browsing the bucket directly.
    """
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    return f"users/{user_id}/{uuid.uuid4()}_{safe_filename}"


def upload_fileobj(file_obj: BinaryIO, key: str, content_type: str | None = None) -> None:
    if not settings.S3_BUCKET_NAME:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3_BUCKET_NAME is not configured on the server.",
        )
    extra_args = {"ContentType": content_type} if content_type else {}
    try:
        get_s3_client().upload_fileobj(
            file_obj, settings.S3_BUCKET_NAME, key, ExtraArgs=extra_args
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload file to S3: {e}",
        )


def delete_object(key: str) -> None:
    try:
        get_s3_client().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to delete file from S3: {e}",
        )


def generate_presigned_download_url(key: str, expires_in: int = 3600) -> str:
    try:
        return get_s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate download link: {e}",
        )

def download_fileobj(key: str) -> bytes:
    """Downloads an S3 object and returns its raw bytes."""
    try:
        response = get_s3_client().get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        return response["Body"].read()
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to download file from S3: {e}",
        )