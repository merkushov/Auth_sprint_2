"""init_migration

Revision ID: 45d9ab32fa85
Revises: 
Create Date: 2022-11-11 23:34:06.877064

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '45d9ab32fa85'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create schema auth')


def downgrade():
    op.execute('drop schema auth')

