"""init migration.

Revision ID: b98f2ccba9e2
Revises:
Create Date: 2022-01-13 12:57:32.228218
"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "b98f2ccba9e2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    op.create_table(
        "login_history",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column(
            "user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True
        ),
        sa.Column("info", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_login_history_user_id"),
        "login_history",
        ["user_id"],
        unique=False,
        schema="auth",
    )
    op.create_table(
        "refresh_jwt",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column(
            "user_id",
            sqlalchemy_utils.types.uuid.UUIDType(binary=False),
            nullable=False,
        ),
        sa.Column("expire", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", "user_id"),
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_refresh_jwt_user_id"),
        "refresh_jwt",
        ["user_id"],
        unique=False,
        schema="auth",
    )
    op.create_table(
        "role",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_role_name"), "role", ["name"], unique=True, schema="auth"
    )
    op.create_table(
        "user",
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        op.f("ix_auth_user_email"), "user", ["email"], unique=True, schema="auth"
    )
    op.create_index(
        op.f("ix_auth_user_username"), "user", ["username"], unique=True, schema="auth"
    )
    op.create_table(
        "user_role",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column(
            "role_id",
            sqlalchemy_utils.types.uuid.UUIDType(binary=False),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sqlalchemy_utils.types.uuid.UUIDType(binary=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["auth.role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.user.id"],
        ),
        sa.PrimaryKeyConstraint("id", "role_id", "user_id"),
        schema="auth",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_role", schema="auth")
    op.drop_index(op.f("ix_auth_user_username"), table_name="user", schema="auth")
    op.drop_index(op.f("ix_auth_user_email"), table_name="user", schema="auth")
    op.drop_table("user", schema="auth")
    op.drop_index(op.f("ix_auth_role_name"), table_name="role", schema="auth")
    op.drop_table("role", schema="auth")
    op.drop_index(
        op.f("ix_auth_refresh_jwt_user_id"), table_name="refresh_jwt", schema="auth"
    )
    op.drop_table("refresh_jwt", schema="auth")
    op.drop_index(
        op.f("ix_auth_login_history_user_id"), table_name="login_history", schema="auth"
    )
    op.drop_table("login_history", schema="auth")
    # ### end Alembic commands ###
