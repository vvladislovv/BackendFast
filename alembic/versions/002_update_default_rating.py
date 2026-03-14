"""Update default rating from 0 to 1

Revision ID: 002
Revises: 001
Create Date: 2026-03-14 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Обновляем существующие записи с rating=0 на rating=1
    op.execute("UPDATE vacancies SET rating = 1 WHERE rating = 0")
    op.execute("UPDATE reviews SET rating = 1 WHERE rating = 0")
    op.execute("UPDATE articles SET rating = 1 WHERE rating = 0")
    op.execute("UPDATE cases SET rating = 1 WHERE rating = 0")
    
    # Изменяем дефолтное значение для новых записей
    op.alter_column('vacancies', 'rating', server_default='1')
    op.alter_column('reviews', 'rating', server_default='1')
    op.alter_column('articles', 'rating', server_default='1')
    op.alter_column('cases', 'rating', server_default='1')


def downgrade() -> None:
    """Downgrade database schema."""
    # Возвращаем дефолтное значение 
обратно на 0
    op.alter_column('vacancies', 'rating', server_default='0')
    op.alter_column('reviews', 'rating', server_default='0')
    op.alter_column('articles', 'rating', server_default='0')
    op.alter_column('cases', 'rating', server_default='0')
