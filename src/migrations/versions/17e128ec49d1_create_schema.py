"""create schema.

Revision ID: 17e128ec49d1
Revises: 280bb904d529
Create Date: 2022-11-09 23:36:08.591951
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '17e128ec49d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create schema auth")


def downgrade():
    op.execute("drop schema auth")

