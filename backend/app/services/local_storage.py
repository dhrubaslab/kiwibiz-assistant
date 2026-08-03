"""
Local filesystem storage backend — used when STORAGE_BACKEND = "local".

Mirrors app/services/s3.py's function shapes (save/delete/path-for-a-key)
so app/services/storage.py can dispatch to either one without the calling
code (documents.py) needing to know which backend is active.

Files are saved under LOCAL_STORAGE_DIR, inside the same
users/<user_id>/<uuid>_<filename> key structure S3 would use.
"""

import shutil
from pathlib import Path
from typing import BinaryIO

from app.config import settings


def _base_dir() -> Path:
    base = Path(settings.LOCAL_STORAGE_DIR)
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_file(file_obj: BinaryIO, key: str, content_type: str | None = None) -> None:
    dest = _base_dir() / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file_obj, out)


def delete_file(key: str) -> None:
    dest = _base_dir() / key
    if dest.exists():
        dest.unlink()


def file_path_for_key(key: str) -> Path:
    return _base_dir() / key
