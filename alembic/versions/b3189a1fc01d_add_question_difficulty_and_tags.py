"""add question difficulty and tags

Revision ID: b3189a1fc01d
Revises: 27afee019656
Create Date: 2026-11-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3189a1fc01d'
down_revision: Union[str, Sequence[str], None] = '27afee019656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('QuestionDB', sa.Column('difficulty', sa.Integer(), server_default='1', nullable=False))
    op.add_column('QuestionDB', sa.Column('tags', sa.JSON(), server_default='[]', nullable=False))


def downgrade() -> None:
    op.drop_column('QuestionDB', 'tags')
    op.drop_column('QuestionDB', 'difficulty')
