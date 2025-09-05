"""
OTP service for OTP generation and verification
"""
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.auth import OTPLog
from app.core.security import generate_otp
from app.core.config import get_settings
from app.core.exceptions import DatabaseError, ValidationError
from .base import BaseService
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class OTPService(BaseService[OTPLog]):
    """OTP service for OTP management"""
    
    def __init__(self):
        super().__init__(OTPLog)
        self.otp_length = 6
        self.otp_expiry_minutes = settings.otp_expire_minutes
        self.max_otp_attempts = 3
        self.otp_cooldown_minutes = 1
    
    def generate_otp_code(self) -> str:
        """Generate OTP code"""
        return generate_otp(self.otp_length)
    
    def create_otp_log(self, db: Session, phone: str) -> Tuple[OTPLog, str]:
        """Create OTP log entry"""
        try:
            # Check for recent OTP attempts
            recent_otp = db.query(OTPLog).filter(
                and_(
                    OTPLog.phone == phone,
                    OTPLog.created_at > datetime.utcnow() - timedelta(minutes=self.otp_cooldown_minutes)
                )
            ).first()
            
            if recent_otp:
                raise ValidationError(f"Please wait {self.otp_cooldown_minutes} minutes before requesting another OTP")
            
            # Check for too many attempts
            recent_attempts = db.query(OTPLog).filter(
                and_(
                    OTPLog.phone == phone,
                    OTPLog.created_at > datetime.utcnow() - timedelta(hours=1)
                )
            ).count()
            
            if recent_attempts >= self.max_otp_attempts:
                raise ValidationError("Too many OTP attempts. Please try again later.")
            
            otp_code = self.generate_otp_code()
            expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            otp_log = OTPLog(
                phone=phone,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            db.add(otp_log)
            db.commit()
            db.refresh(otp_log)
            
            return otp_log, otp_code
        except Exception as e:
            logger.error(f"Error creating OTP log for {phone}: {e}")
            db.rollback()
            if isinstance(e, ValidationError):
                raise
            raise DatabaseError("Failed to create OTP log")
    
    def verify_otp(self, db: Session, phone: str, otp: str) -> Optional[OTPLog]:
        """Verify OTP code"""
        try:
            otp_log = db.query(OTPLog).filter(
                and_(
                    OTPLog.phone == phone,
                    OTPLog.otp_code == otp,
                    OTPLog.is_verified == False,
                    OTPLog.expires_at > datetime.utcnow()
                )
            ).order_by(OTPLog.created_at.desc()).first()
            
            if otp_log:
                otp_log.is_verified = True
                db.commit()
                return otp_log
            return None
        except Exception as e:
            logger.error(f"Error verifying OTP for {phone}: {e}")
            db.rollback()
            raise DatabaseError("Failed to verify OTP")
    
    def get_latest_otp(self, db: Session, phone: str) -> Optional[OTPLog]:
        """Get the latest OTP for a phone number"""
        try:
            return db.query(OTPLog).filter(
                OTPLog.phone == phone
            ).order_by(OTPLog.created_at.desc()).first()
        except Exception as e:
            logger.error(f"Error getting latest OTP for {phone}: {e}")
            raise DatabaseError("Failed to retrieve OTP")
    
    def cleanup_expired_otps(self, db: Session) -> int:
        """Clean up expired OTP logs"""
        try:
            expired_otps = db.query(OTPLog).filter(
                OTPLog.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired_otps)
            for otp in expired_otps:
                db.delete(otp)
            
            db.commit()
            logger.info(f"Cleaned up {count} expired OTP logs")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {e}")
            db.rollback()
            raise DatabaseError("Failed to cleanup expired OTPs")
    
    def send_otp_sms(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS (mock implementation)"""
        try:
            # TODO: Integrate with actual SMS provider (Twilio, AWS SNS, etc.)
            logger.info(f"OTP {otp} sent to {phone}")
            
            # Mock SMS sending
            # In production, integrate with SMS provider
            # sms_provider = get_sms_provider()
            # return sms_provider.send_sms(phone, f"Your TimelyCabs OTP is: {otp}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP to {phone}: {str(e)}")
            return False
    
    def get_otp_statistics(self, db: Session, phone: Optional[str] = None) -> dict:
        """Get OTP statistics"""
        try:
            query = db.query(OTPLog)
            if phone:
                query = query.filter(OTPLog.phone == phone)
            
            total_otps = query.count()
            verified_otps = query.filter(OTPLog.is_verified == True).count()
            expired_otps = query.filter(OTPLog.expires_at < datetime.utcnow()).count()
            
            return {
                "total_otps": total_otps,
                "verified_otps": verified_otps,
                "expired_otps": expired_otps,
                "verification_rate": (verified_otps / total_otps * 100) if total_otps > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting OTP statistics: {e}")
            raise DatabaseError("Failed to retrieve OTP statistics")
