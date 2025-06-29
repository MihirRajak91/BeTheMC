"""
Authentication models for BeTheMC.

This module defines the Pydantic models used for authentication requests and responses.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload model."""
    username: Optional[str] = None
    scopes: list[str] = []


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    """User model for database operations."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    """User response model (without sensitive data)."""
    id: str
    created_at: datetime
    updated_at: datetime
