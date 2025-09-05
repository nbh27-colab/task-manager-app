# api/schemas/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base schema for user, containing common fields."""
    email: EmailStr

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

class UserInDBBase(UserBase):
    """Base schema for user data as stored in the database."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # For Pydantic v2+, use from_attributes=True instead of orm_mode=True

class User(UserInDBBase):
    """Schema for user data returned to the client (excludes hashed password)."""
    pass

class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str
