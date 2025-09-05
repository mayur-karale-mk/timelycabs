"""
Base model classes and common fields
"""
from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PrimaryKeyMixin:
    """Mixin for primary key with auto-increment"""
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
