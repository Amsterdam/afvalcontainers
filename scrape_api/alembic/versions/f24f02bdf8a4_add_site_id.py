"""
Empty start. right after default models are created we put alembic on this
version

Revision ID: f24f02bdf8a4
Revises:
Create Date: 2019-01-17 16:02:04.871329
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f24f02bdf8a4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
