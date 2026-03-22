"""Add content field to articles

Revision ID: 003
Revises: 002
Create Date: 2026-03-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле content в таблицу articles
    op.add_column('articles', sa.Column('content', sa.Text(), nullable=False, server_default=''))


def downgrade() -> None:
    # Удаляем поле content из таблицы articles
    op.drop_column('articles', 'content')
