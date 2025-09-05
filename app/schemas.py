"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import GenderEnum, RoleEnum

# Request Schemas

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
    gender: GenderEnum = Field(..., description="User's gender")

class LogoutRequest(BaseModel):
    """Request schema for logout"""
    auth_token: str = Field(..., description="Authentication token to invalidate")

# Response Schemas

class UserResponse(BaseModel):
    """User information response"""
    user_id: int
    full_name: Optional[str]
    gender: Optional[str]
    phone: str
    phone_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    """Role information response"""
    role_id: int
    role_name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class UserWithRolesResponse(BaseModel):
    """User with roles response"""
    user_id: int
    full_name: Optional[str]
    gender: Optional[str]
    phone: str
    phone_verified: bool
    is_active: bool
    created_at: datetime
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True

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

# Error Response Schema

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
