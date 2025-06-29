"""
MongoDB models for authentication.

This module defines the Pydantic models for MongoDB documents.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(UserBase):
    """User creation model with password."""
    password: str


class UserInDB(UserBase):
    """User model for database operations."""
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def is_active(self) -> bool:
        """Check if the user is active."""
        return not self.disabled

    def dict(self, **kwargs):
        """Convert model to dictionary, including computed fields."""
        data = super().dict(**kwargs)
        data['id'] = data.pop('_id')  # Use 'id' instead of '_id' in API responses
        return data
