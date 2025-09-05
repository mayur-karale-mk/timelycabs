"""
Custom exceptions for the application
"""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class TimelyCabsException(Exception):
    """Base exception for TimelyCabs application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(TimelyCabsException):
    """Authentication related errors"""
    pass


class AuthorizationError(TimelyCabsException):
    """Authorization related errors"""
    pass


class ValidationError(TimelyCabsException):
    """Data validation errors"""
    pass


class DatabaseError(TimelyCabsException):
    """Database related errors"""
    pass


class ExternalServiceError(TimelyCabsException):
    """External service errors"""
    pass


class BusinessLogicError(TimelyCabsException):
    """Business logic errors"""
    pass


# HTTP Exception mappings
def create_http_exception(
    exception: TimelyCabsException,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> HTTPException:
    """Convert TimelyCabsException to HTTPException"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exception.message,
            "error_code": exception.error_code,
            "details": exception.details
        }
    )


# Common HTTP exceptions
class NotFoundError(HTTPException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class ConflictError(HTTPException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class BadRequestError(HTTPException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class InternalServerError(HTTPException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
