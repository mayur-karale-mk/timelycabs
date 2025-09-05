"""
Authentication service for OTP-based authentication
"""
import random
import string
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import User, OTPLog, Session as UserSession, Role, UserRole
from app.schemas import GenderEnum
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        self.session_expiry_days = 7
        self.temp_token_expiry_minutes = 10
    
    def generate_otp(self) -> str:
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def generate_auth_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def create_otp_log(self, db: Session, phone: str) -> Tuple[OTPLog, str]:
        otp_code = self.generate_otp()
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
    
    def verify_otp(self, db: Session, phone: str, otp: str) -> Optional[OTPLog]:
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
    
    def get_user_by_phone(self, db: Session, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()
    
    def create_user(self, db: Session, phone: str) -> User:
        user = User(phone=phone, phone_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        self.assign_default_role(db, user.user_id)
        return user
    
    def assign_default_role(self, db: Session, user_id: int):
        rider_role = db.query(Role).filter(Role.role_name == "rider").first()
        if rider_role:
            user_role = UserRole(user_id=user_id, role_id=rider_role.role_id)
            db.add(user_role)
            db.commit()
    
    def update_user_profile(self, db: Session, user_id: int, full_name: str, gender: GenderEnum) -> User:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.full_name = full_name
            user.gender = gender
            user.phone_verified = True
            db.commit()
            db.refresh(user)
        return user
    
    def create_session(self, db: Session, user_id: int, device_info: Optional[str] = None, is_temp: bool = False) -> UserSession:
        auth_token = self.generate_auth_token()
        
        if is_temp:
            expires_at = datetime.utcnow() + timedelta(minutes=self.temp_token_expiry_minutes)
        else:
            expires_at = datetime.utcnow() + timedelta(days=self.session_expiry_days)
        
        session = UserSession(
            user_id=user_id,
            auth_token=auth_token,
            device_info=device_info,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def get_session_by_token(self, db: Session, auth_token: str) -> Optional[UserSession]:
        return db.query(UserSession).filter(
            and_(
                UserSession.auth_token == auth_token,
                or_(
                    UserSession.expires_at > datetime.utcnow(),
                    UserSession.expires_at.is_(None)
                )
            )
        ).first()
    
    def delete_session(self, db: Session, auth_token: str) -> bool:
        session = db.query(UserSession).filter(UserSession.auth_token == auth_token).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    def get_user_with_roles(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()
    
    def send_otp_sms(self, phone: str, otp: str) -> bool:
        try:
            logger.info(f"OTP {otp} sent to {phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP to {phone}: {str(e)}")
            return False

auth_service = AuthService()
