"""
Authentication-related schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

from .user import UserWithRolesResponse


class RequestOTPRequest(BaseModel):
    """Request schema for OTP generation"""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number with country code")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if not v[1:].isdigit():
            raise ValueError('Phone number must contain only digits after +')
        return v


class VerifyOTPRequest(BaseModel):
    """Request schema for OTP verification"""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number with country code")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    device_info: Optional[str] = Field(None, max_length=255, description="Device information")


class CompleteProfileRequest(BaseModel):
    """Request schema for profile completion"""
    auth_token: str = Field(..., description="Temporary authentication token")
    full_name: str = Field(..., min_length=2, max_length=150, description="User's full name")
    gender: str = Field(..., description="User's gender")


class LogoutRequest(BaseModel):
    """Request schema for logout"""
    auth_token: str = Field(..., description="Authentication token to invalidate")


class RequestOTPResponse(BaseModel):
    """Response schema for OTP request"""
    success: bool
    message: str
    otp_id: Optional[int] = None


class VerifyOTPResponse(BaseModel):
    """Response schema for OTP verification"""
    success: bool
    message: str
    is_new_user: Optional[bool] = None
    phone: Optional[str] = None
    auth_token: Optional[str] = None
    user: Optional[UserWithRolesResponse] = None


class CompleteProfileResponse(BaseModel):
    """Response schema for profile completion"""
    success: bool
    message: str
    user: UserWithRolesResponse
    auth_token: str


class LogoutResponse(BaseModel):
    """Response schema for logout"""
    success: bool
    message: str
