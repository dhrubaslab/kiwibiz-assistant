"""fix message_role enum casing

Revision ID: 6ac615433ac1
Revises: 4a8c60ee768a
Create Date: 2026-09-03 15:12:30.335896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ac615433ac1'
down_revision: Union[str, None] = '4a8c60ee768a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE message_role RENAME VALUE 'user' TO 'USER'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'assistant' TO 'ASSISTANT'")
 
 
def downgrade() -> None:
    op.execute("ALTER TYPE message_role RENAME VALUE 'USER' TO 'user'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'ASSISTANT' TO 'assistant'")
