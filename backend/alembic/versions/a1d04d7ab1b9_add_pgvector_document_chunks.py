"""add pgvector document chunks

Revision ID: a1d04d7ab1b9
Revises: e654e1c8d586
Create Date: 2026-08-23 12:11:18.955465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'a1d04d7ab1b9'
down_revision: Union[str, None] = 'e654e1c8d586'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# OpenAI text-embedding-3-small produces 1536-dim vectors.
EMBEDDING_DIM = 1536


def upgrade() -> None:
    # 1. Enable the pgvector extension (idempotent — safe to run if already enabled)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Create the document_chunks table
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
    )

    # 3. Approximate nearest-neighbour index (IVFFlat) for fast similarity search.
    # `lists` is a tuning parameter — 100 is a reasonable default for a small/medium
    # corpus. This can be rebuilt later with a higher value as the document count grows.
    op.execute(
        """
        CREATE INDEX ix_document_chunks_embedding
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    # Not dropping the extension itself in downgrade — other tables/migrations
    # may depend on it, and CREATE EXTENSION IF NOT EXISTS is safe to leave in place.


# ---------------------------------------------------------------------------
# NOTE on the Postgres image: if `CREATE EXTENSION vector` fails with something
# like "could not open extension control file", your kiwi-biz-db container's
# Postgres image doesn't have pgvector compiled in. You'll need to switch to
# the pgvector/pgvector:pg16 image (or whatever major version you're on) in
# your docker-compose / run command, e.g.:
#
#   docker run --name kiwi-biz-db -e POSTGRES_PASSWORD=... \
#     -p 5432:5432 -v kiwi_biz_data:/var/lib/postgresql/data \
#     -d pgvector/pgvector:pg16
#
# This is a drop-in replacement for the standard postgres image — your
# existing data volume is unaffected since the extension is added to the
# database, not baked into the data files.
# ---------------------------------------------------------------------------
