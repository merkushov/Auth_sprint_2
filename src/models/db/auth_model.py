"""Модели для SQLAlchemy."""

import datetime
import enum
import uuid

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType, UUIDType

from db import db

# turn off cache for UUIDType to supress warning in newer versions
# more info needed before turning this one as it possibly
# slows down the app if False
UUIDType.cache_ok = False


class SocialType(enum.Enum):
    FB = 0
    GOOGLE = 1
    YANDEX = 2
    SELF = 3


def generate_uuid():
    return uuid.uuid4()


class Base(db.Model):
    """Базовая модель."""

    __abstract__ = True
    __table_args__ = {"schema": "auth"}

    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime)


class LoginHistory(Base):
    """История входов пользователя."""

    __tablename__ = "login_history"

    id = db.Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)
    user_id = db.Column(UUIDType(binary=False), index=True)
    info = db.Column(db.Text(), nullable=True)
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    # partitioning
    #


class RefreshJwt(Base):
    """Модель рефреш токена для пользователя."""

    __tablename__ = "refresh_jwt"

    id = db.Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)
    user_id = db.Column(UUIDType(binary=False), index=True, primary_key=True)
    expire = db.Column(DateTime)


class Role(Base):
    """Пользовательские роли."""

    __tablename__ = "role"

    id = db.Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)
    name = db.Column(db.Text(), index=True, unique=True)

    def __repr__(self):
        return f"{self.name}"


user_role = db.Table(
    "user_role",
    db.Model.metadata,
    db.Column("id", UUIDType(binary=False), primary_key=True, default=generate_uuid),
    db.Column("role_id", db.ForeignKey("auth.role.id"), primary_key=True),
    db.Column("user_id", db.ForeignKey("auth.user.id"), primary_key=True),
    db.Column("created_at", DateTime, default=datetime.datetime.utcnow),
    schema="auth",
)


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"

    id = db.Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)
    username = db.Column(db.Text(), index=True, unique=True)
    email = db.Column(db.Text(), index=True, unique=True)
    password_hash = db.Column(db.Text())
    roles = relationship("Role", secondary=user_role)
    social_accounts = relationship('SocialAccount')

    def __repr__(self):
        return f"<User {self.username}>"


class SocialAccount(Base):
    """История входов через социальные сервисы."""
    __tablename__ = 'social_account'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    id = db.Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(
        ChoiceType(SocialType, impl=db.Integer()),
        comment="Тип социального сервиса",
        nullable=False,
    )

