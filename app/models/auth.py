"""
Authentication-related models
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, TimestampMixin, PrimaryKeyMixin


class OTPLog(Base, TimestampMixin):
    """OTP Log model"""
    __tablename__ = "otp_logs"
    
    otp_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<OTPLog(otp_id={self.otp_id}, phone='{self.phone}')>"


class Session(Base, TimestampMixin):
    """Session model"""
    __tablename__ = "sessions"
    
    session_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    auth_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id})>"
