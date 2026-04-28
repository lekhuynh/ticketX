"""alter ai_docs embedding dimension to 768

Revision ID: a5e2d4c3b1f0
Revises: 7b9b4842f9f1
Create Date: 2026-04-02 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a5e2d4c3b1f0'
down_revision = '7b9b4842f9f1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE ai_docs ALTER COLUMN embedding TYPE vector(768) USING embedding::vector(768)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE ai_docs ALTER COLUMN embedding TYPE vector(1024) USING embedding::vector(1024)"
    )
