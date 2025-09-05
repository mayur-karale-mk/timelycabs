"""
Authentication service for user authentication and session management
"""
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User, Role, UserRole
from app.models.auth import Session as UserSession
from app.core.security import generate_secure_token
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, DatabaseError
from .base import BaseService
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService(BaseService[User]):
    """Authentication service"""
    
    def __init__(self):
        super().__init__(User)
        self.session_expiry_days = settings.refresh_token_expire_days
        self.temp_token_expiry_minutes = 10
    
    def get_user_by_phone(self, db: Session, phone: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            return db.query(User).filter(User.phone == phone).first()
        except Exception as e:
            logger.error(f"Error getting user by phone {phone}: {e}")
            raise DatabaseError("Failed to retrieve user")
    
    def create_user(self, db: Session, phone: str) -> User:
        """Create a new user"""
        try:
            user = User(phone=phone, phone_verified=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Assign default rider role
            self.assign_default_role(db, user.user_id)
            return user
        except Exception as e:
            logger.error(f"Error creating user with phone {phone}: {e}")
            db.rollback()
            raise DatabaseError("Failed to create user")
    
    def assign_default_role(self, db: Session, user_id: int) -> bool:
        """Assign default rider role to user"""
        try:
            rider_role = db.query(Role).filter(Role.role_name == "rider").first()
            if not rider_role:
                # Create default roles if they don't exist
                self.create_default_roles(db)
                rider_role = db.query(Role).filter(Role.role_name == "rider").first()
            
            if rider_role:
                user_role = UserRole(user_id=user_id, role_id=rider_role.role_id)
                db.add(user_role)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error assigning default role to user {user_id}: {e}")
            db.rollback()
            raise DatabaseError("Failed to assign default role")
    
    def create_default_roles(self, db: Session) -> None:
        """Create default roles if they don't exist"""
        try:
            default_roles = [
                {"role_name": "rider", "description": "Regular user who books rides"},
                {"role_name": "driver", "description": "Driver who provides rides"},
                {"role_name": "owner", "description": "Fleet owner"},
                {"role_name": "admin", "description": "System administrator"},
                {"role_name": "support", "description": "Customer support"}
            ]
            
            for role_data in default_roles:
                existing_role = db.query(Role).filter(Role.role_name == role_data["role_name"]).first()
                if not existing_role:
                    role = Role(**role_data)
                    db.add(role)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error creating default roles: {e}")
            db.rollback()
            raise DatabaseError("Failed to create default roles")
    
    def update_user_profile(
        self, 
        db: Session, 
        user_id: int, 
        full_name: str, 
        gender: str
    ) -> Optional[User]:
        """Update user profile information"""
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.full_name = full_name
                user.gender = gender
                user.phone_verified = True
                db.commit()
                db.refresh(user)
                return user
            return None
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            db.rollback()
            raise DatabaseError("Failed to update user profile")
    
    def create_session(
        self, 
        db: Session, 
        user_id: int, 
        device_info: Optional[str] = None, 
        is_temp: bool = False
    ) -> UserSession:
        """Create a new user session"""
        try:
            auth_token = generate_secure_token()
            
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
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            db.rollback()
            raise DatabaseError("Failed to create session")
    
    def get_session_by_token(self, db: Session, auth_token: str) -> Optional[UserSession]:
        """Get session by authentication token"""
        try:
            return db.query(UserSession).filter(
                and_(
                    UserSession.auth_token == auth_token,
                    or_(
                        UserSession.expires_at > datetime.utcnow(),
                        UserSession.expires_at.is_(None)
                    )
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting session by token: {e}")
            raise DatabaseError("Failed to retrieve session")
    
    def delete_session(self, db: Session, auth_token: str) -> bool:
        """Delete a session by token"""
        try:
            session = db.query(UserSession).filter(UserSession.auth_token == auth_token).first()
            if session:
                db.delete(session)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            db.rollback()
            raise DatabaseError("Failed to delete session")
    
    def get_user_with_roles(self, db: Session, user_id: int) -> Optional[User]:
        """Get user with their roles"""
        try:
            from sqlalchemy.orm import joinedload
            return db.query(User).options(
                joinedload(User.user_roles).joinedload(UserRole.role)
            ).filter(User.user_id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user with roles {user_id}: {e}")
            raise DatabaseError("Failed to retrieve user with roles")
    
    def validate_session(self, db: Session, auth_token: str) -> Optional[User]:
        """Validate session and return user"""
        session = self.get_session_by_token(db, auth_token)
        if session:
            return self.get_user_with_roles(db, session.user_id)
        return None
