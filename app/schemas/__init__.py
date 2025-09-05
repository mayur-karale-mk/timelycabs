"""
Pydantic schemas package
"""
from .auth import (
    RequestOTPRequest,
    VerifyOTPRequest,
    CompleteProfileRequest,
    LogoutRequest,
    RequestOTPResponse,
    VerifyOTPResponse,
    CompleteProfileResponse,
    LogoutResponse
)
from .user import (
    UserResponse,
    RoleResponse,
    UserWithRolesResponse
)
from .common import (
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    PaginatedResponse
)

__all__ = [
    # Auth schemas
    "RequestOTPRequest",
    "VerifyOTPRequest", 
    "CompleteProfileRequest",
    "LogoutRequest",
    "RequestOTPResponse",
    "VerifyOTPResponse",
    "CompleteProfileResponse",
    "LogoutResponse",
    
    # User schemas
    "UserResponse",
    "RoleResponse",
    "UserWithRolesResponse",
    
    # Common schemas
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse"
]
