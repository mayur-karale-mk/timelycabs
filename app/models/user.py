"""
User-related models
"""
from sqlalchemy import Column, String, Boolean, BigInteger, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, TimestampMixin, PrimaryKeyMixin


class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=True)
    gender = Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=True)
    phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, phone='{self.phone}')>"


class Role(Base):
    """Role model"""
    __tablename__ = "roles"
    
    role_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    role_name = Column(Enum('rider', 'driver', 'owner', 'admin', 'support', name='role_enum'), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    
    def __repr__(self):
        return f"<Role(role_id={self.role_id}, role_name='{self.role_name}')>"


class UserRole(Base, TimestampMixin):
    """UserRole model - many-to-many relationship between users and roles"""
    __tablename__ = "user_roles"
    
    user_role_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    
    def __repr__(self):
        return f"<UserRole(user_role_id={self.user_role_id}, user_id={self.user_id}, role_id={self.role_id})>"
