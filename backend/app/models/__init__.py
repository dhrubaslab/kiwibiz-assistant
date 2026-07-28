# Import every model here so Alembic's autogenerate can discover them
# via Base.metadata (see alembic/env.py).

from app.models.user import User  # noqa: F401
from app.models.document import Document, DocumentStatus  # noqa: F401
