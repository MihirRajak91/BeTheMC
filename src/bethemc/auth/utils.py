"""
Authentication utility functions.

This module contains helper functions for authentication.
"""
import re
from typing import Optional

from pydantic import EmailStr, validator
from pydantic.validators import str_validator


class Username(str):
    """Custom username type with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        v = v.strip()
        if len(v) < 3:
            raise ValueError('username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('username must be at most 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('username can only contain letters, numbers, and underscores')
        
        return cls(v)


def validate_password_strength(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")
    return True


def sanitize_email(email: str) -> str:
    """Sanitize and validate an email address."""
    return EmailStr.validate(email).lower().strip()


def generate_username_from_email(email: str) -> str:
    """Generate a username from an email address."""
    # Extract the part before @ and clean it up
    username = email.split('@')[0]
    # Remove any non-alphanumeric characters and convert to lowercase
    username = re.sub(r'[^a-zA-Z0-9]', '', username).lower()
    # Ensure the username meets minimum length requirements
    if len(username) < 3:
        username = username + 'user'
    return username
