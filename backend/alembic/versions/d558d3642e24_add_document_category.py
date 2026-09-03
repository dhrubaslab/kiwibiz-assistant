"""add document category

Revision ID: d558d3642e24
Revises: 6ac615433ac1
Create Date: 2026-09-03 17:07:32.234754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd558d3642e24'
down_revision: Union[str, None] = '6ac615433ac1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Enum stored uppercase (member NAME), matching document_status and the
    # now-corrected message_role convention — SQLAlchemy's Enum column type
    # sends the Python member name, not .value, by default.
    document_category = postgresql.ENUM(
        "POLICY", "CONTRACT", "FINANCIAL", "HR", "OTHER",
        name="document_category",
    )
    document_category.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "documents",
        sa.Column(
            "category",
            document_category,
            nullable=False,
            server_default="OTHER",
        ),
    )
    # Drop the server default now that existing rows are backfilled — new
    # rows will always specify a category explicitly via the model default.
    op.alter_column("documents", "category", server_default=None)


def downgrade() -> None:
    op.drop_column("documents", "category")
    op.execute("DROP TYPE IF EXISTS document_category")