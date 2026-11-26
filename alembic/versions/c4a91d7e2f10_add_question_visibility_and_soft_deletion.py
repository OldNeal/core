"""add question visibility and soft deletion flags

Revision ID: c4a91d7e2f10
Revises: b3189a1fc01d
Create Date: 2026-11-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4a91d7e2f10'
down_revision: Union[str, Sequence[str], None] = 'b3189a1fc01d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('QuestionDB', sa.Column('is_hidden', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('QuestionDB', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    op.drop_column('QuestionDB', 'is_deleted')
    op.drop_column('QuestionDB', 'is_hidden')
