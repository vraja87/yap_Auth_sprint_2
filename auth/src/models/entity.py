import uuid
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, String,
                        Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base

"""
Db models. Used in code and in alembic migrations.

dnt forget to make migrations
"""


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "content"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship('Role', secondary='content.user_roles', back_populates='users')
    tokens = relationship('RefreshToken', back_populates='user')
    login_histories = relationship('LoginHistory', back_populates='user')

    def __init__(self, login: str, password: str, first_name: str | None = None, last_name: str | None = None) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserRoles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = {"schema": "content"}

    user_id = Column(UUID(as_uuid=True), ForeignKey('content.users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('content.roles.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "content"}

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    users = relationship('User', secondary='content.user_roles', back_populates='roles')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name: str, description: str | None) -> None:
        self.name = name
        self.description = description


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (
        Index('idx_refresh_tokens_token', 'jwt_token', 'user_agent'),
        {"schema": "content"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('content.users.id', ondelete='CASCADE'))
    jwt_token = Column(Text, index=True)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    is_valid = Column(Boolean, default=False)
    user = relationship('User', back_populates='tokens')


class LoginHistory(Base):
    __tablename__ = 'login_histories'
    __table_args__ = {"schema": "content"}

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('content.users.id', ondelete='CASCADE'))
    user_agent = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='login_histories')

    def __init__(self, user_id: UUID, user_agent: str, ip_address: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.ip_address = ip_address
