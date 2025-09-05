"""
User-related schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RoleResponse(BaseModel):
    """Role response schema"""
    role_id: int
    role_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response schema"""
    user_id: int
    phone: str
    full_name: Optional[str] = None
    gender: Optional[str] = None
    phone_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserWithRolesResponse(BaseModel):
    """User response schema with roles"""
    user_id: int
    phone: str
    full_name: Optional[str] = None
    gender: Optional[str] = None
    phone_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True
