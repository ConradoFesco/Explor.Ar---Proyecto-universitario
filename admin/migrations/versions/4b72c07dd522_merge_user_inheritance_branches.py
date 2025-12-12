"""Merge user inheritance and deletion_reason branches

Revision ID: 4b72c07dd522
Revises: ('a7b77b58a3e5', '7c3a9f0f1d23')
Create Date: 2025-12-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4b72c07dd522'
down_revision = ('a7b77b58a3e5', '7c3a9f0f1d23')
branch_labels = None
depends_on = None


def upgrade():
    # Esta es una migración de merge, no necesita cambios adicionales
    # Las dos ramas ya están combinadas en esta migración
    pass


def downgrade():
    # Migración de merge, no requiere rollback específico
    pass

