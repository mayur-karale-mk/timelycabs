"""
SQLAlchemy models for the authentication system
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class GenderEnum(enum.Enum):
    """Gender enumeration"""
    male = "male"
    female = "female"
    other = "other"

class RoleEnum(enum.Enum):
    """Role enumeration"""
    rider = "rider"
    driver = "driver"
    owner = "owner"
    admin = "admin"
    support = "support"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    sessions = relationship("Session", back_populates="user")

class Role(Base):
    """Role model"""
    __tablename__ = "roles"
    
    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(Enum(RoleEnum), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")

class UserRole(Base):
    """User-Role relationship model"""
    __tablename__ = "user_roles"
    
    user_role_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

class OTPLog(Base):
    """OTP Log model"""
    __tablename__ = "otp_logs"
    
    otp_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    """Session model"""
    __tablename__ = "sessions"
    
    session_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    auth_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
