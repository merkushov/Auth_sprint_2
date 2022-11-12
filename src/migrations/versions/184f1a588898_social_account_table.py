"""social account table

Revision ID: 184f1a588898
Revises: 12d07c9dc79e
Create Date: 2022-11-12 11:55:17.977192

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '184f1a588898'
down_revision = '12d07c9dc79e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('social_account',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True),
    sa.Column('social_id', sa.Text(), nullable=False),
    sa.Column('social_name', sa.Text(), nullable=False, comment='Тип социального сервиса'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_id', 'social_name', name='social_pk')
    )


def downgrade():
    op.drop_table('social_account')
    # ### end Alembic commands ###
