"""remove deletion_reason column from User

Revision ID: xxxxxxxxxxxx
Revises: b67685236135
Create Date: 2025-12-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c3a9f0f1d23'
down_revision = 'b67685236135'
branch_labels = None
depends_on = None


def upgrade():
    """Drop deletion_reason column from User."""
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_column('deletion_reason')


def downgrade():
    """Re-add deletion_reason column to User."""
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deletion_reason', sa.String(length=255), nullable=True))


