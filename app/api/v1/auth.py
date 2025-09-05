"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, ValidationError
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.schemas.auth import (
    RequestOTPRequest,
    VerifyOTPRequest,
    CompleteProfileRequest,
    LogoutRequest,
    RequestOTPResponse,
    VerifyOTPResponse,
    CompleteProfileResponse,
    LogoutResponse
)
from app.schemas.common import ErrorResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
auth_service = AuthService()
otp_service = OTPService()


@router.post("/request-otp", response_model=RequestOTPResponse)
async def request_otp(
    request: RequestOTPRequest,
    db: Session = Depends(get_db)
) -> RequestOTPResponse:
    """
    Request OTP for phone number verification
    """
    try:
        # Create OTP log
        otp_log, otp_code = otp_service.create_otp_log(db, request.phone)
        
        # Send OTP via SMS
        sms_sent = otp_service.send_otp_sms(request.phone, otp_code)
        
        if not sms_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP"
            )
        
        return RequestOTPResponse(
            success=True,
            message="OTP sent successfully",
            otp_id=otp_log.otp_id
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error requesting OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
) -> VerifyOTPResponse:
    """
    Verify OTP and authenticate user
    """
    try:
        # Verify OTP
        otp_log = otp_service.verify_otp(db, request.phone, request.otp)
        
        if not otp_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Check if user exists
        user = auth_service.get_user_by_phone(db, request.phone)
        is_new_user = user is None
        
        if is_new_user:
            # Create new user
            user = auth_service.create_user(db, request.phone)
        
        # Create session
        session = auth_service.create_session(
            db, 
            user.user_id, 
            request.device_info,
            is_temp=is_new_user
        )
        
        # Get user with roles
        user_with_roles = auth_service.get_user_with_roles(db, user.user_id)
        
        return VerifyOTPResponse(
            success=True,
            message="OTP verified successfully",
            is_new_user=is_new_user,
            phone=request.phone,
            auth_token=session.auth_token,
            user=user_with_roles
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/complete-profile", response_model=CompleteProfileResponse)
async def complete_profile(
    request: CompleteProfileRequest,
    db: Session = Depends(get_db)
) -> CompleteProfileResponse:
    """
    Complete user profile with name and gender
    """
    try:
        # Validate session
        session = auth_service.get_session_by_token(db, request.auth_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Update user profile
        user = auth_service.update_user_profile(
            db, 
            session.user_id, 
            request.full_name, 
            request.gender
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create permanent session
        permanent_session = auth_service.create_session(
            db, 
            user.user_id, 
            session.device_info,
            is_temp=False
        )
        
        # Delete temporary session
        auth_service.delete_session(db, request.auth_token)
        
        # Get user with roles
        user_with_roles = auth_service.get_user_with_roles(db, user.user_id)
        
        return CompleteProfileResponse(
            success=True,
            message="Profile completed successfully",
            user=user_with_roles,
            auth_token=permanent_session.auth_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
) -> LogoutResponse:
    """
    Logout user and invalidate session
    """
    try:
        success = auth_service.delete_session(db, request.auth_token)
        
        if not success:
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
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
