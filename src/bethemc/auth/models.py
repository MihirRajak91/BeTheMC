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
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class TokenData(BaseModel):
    """
    Token payload model.
    
    Attributes:
        username: User's email address (used as subject, stored as 'username' for backward compatibility)
        exp: Expiration timestamp
        type: Token type ('access' or 'refresh')
    """
    username: str  # This is actually the email, kept as username for backward compatibility
    exp: int  # Expiration timestamp
    type: str = "access"  # 'access' or 'refresh'
    
    # Add email as a property for backward compatibility
    @property
    def email(self) -> str:
        return self.username


class UserBase(BaseModel):
    """
    Base user model with common fields.
    
    Attributes:
        email: User's email address (primary identifier)
        full_name: Optional full name of the user
        disabled: Whether the user account is disabled
    """
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(BaseModel):
    """
    User creation model.
    
    Attributes:
        email: User's email address (must be unique)
        password: Plain text password (will be hashed)
        full_name: Optional full name of the user
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: Optional[str] = None


class UserInDB(UserBase):
    """User model for database operations."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response model (without sensitive data)."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
