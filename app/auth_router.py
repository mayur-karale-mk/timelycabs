from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import and_
from database import get_db
from schemas import *
from auth_service import auth_service
from models import OTPLog
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp", response_model=RequestOTPResponse)
async def request_otp(request: RequestOTPRequest, db: Session = Depends(get_db)):
    try:
        recent_otp = db.query(OTPLog).filter(
            and_(
                OTPLog.phone == request.phone,
                OTPLog.created_at > datetime.utcnow() - timedelta(minutes=1)
            )
        ).first()
        
        if recent_otp:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OTP already sent. Please wait before requesting another."
            )
        
        otp_log, otp_code = auth_service.create_otp_log(db, request.phone)
        sms_sent = auth_service.send_otp_sms(request.phone, otp_code)
        
        if not sms_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )
        
        return RequestOTPResponse(
            success=True,
            message="OTP sent successfully",
            otp_id=otp_log.otp_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        otp_log = auth_service.verify_otp(db, request.phone, request.otp)
        
        if not otp_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        user = auth_service.get_user_by_phone(db, request.phone)
        
        if user:
            session = auth_service.create_session(db, user.user_id, request.device_info, is_temp=False)
            user_with_roles = auth_service.get_user_with_roles(db, user.user_id)
            
            roles = []
            for ur in user_with_roles.roles:
                roles.append(RoleResponse(
                    role_id=ur.role.role_id,
                    role_name=ur.role.role_name.value,
                    description=ur.role.description
                ))
            
            user_response = UserWithRolesResponse(
                user_id=user_with_roles.user_id,
                full_name=user_with_roles.full_name,
                gender=user_with_roles.gender.value if user_with_roles.gender else None,
                phone=user_with_roles.phone,
                phone_verified=user_with_roles.phone_verified,
                is_active=user_with_roles.is_active,
                created_at=user_with_roles.created_at,
                roles=roles
            )
            
            return VerifyOTPResponse(
                success=True,
                message="Login successful",
                user=user_response,
                auth_token=session.auth_token
            )
        else:
            user = auth_service.create_user(db, request.phone)
            session = auth_service.create_session(db, user.user_id, request.device_info, is_temp=True)
            
            return VerifyOTPResponse(
                success=True,
                message="OTP verified, complete profile required",
                is_new_user=True,
                phone=request.phone,
                auth_token=session.auth_token
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/complete-profile", response_model=CompleteProfileResponse)
async def complete_profile(request: CompleteProfileRequest, db: Session = Depends(get_db)):
    try:
        session = auth_service.get_session_by_token(db, request.auth_token)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user = auth_service.update_user_profile(db, session.user_id, request.full_name, request.gender)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        auth_service.delete_session(db, request.auth_token)
        new_session = auth_service.create_session(db, user.user_id, session.device_info, is_temp=False)
        
        user_with_roles = auth_service.get_user_with_roles(db, user.user_id)
        roles = []
        for ur in user_with_roles.roles:
            roles.append(RoleResponse(
                role_id=ur.role.role_id,
                role_name=ur.role.role_name.value,
                description=ur.role.description
            ))
        
        user_response = UserWithRolesResponse(
            user_id=user_with_roles.user_id,
            full_name=user_with_roles.full_name,
            gender=user_with_roles.gender.value if user_with_roles.gender else None,
            phone=user_with_roles.phone,
            phone_verified=user_with_roles.phone_verified,
            is_active=user_with_roles.is_active,
            created_at=user_with_roles.created_at,
            roles=roles
        )
        
        return CompleteProfileResponse(
            success=True,
            message="Profile completed, login successful",
            user=user_response,
            auth_token=new_session.auth_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    try:
        deleted = auth_service.delete_session(db, request.auth_token)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return LogoutResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
