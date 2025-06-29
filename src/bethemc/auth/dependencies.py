"""
Authentication dependencies for FastAPI routes.

This module provides dependencies for handling authentication in API routes,
including token verification and user retrieval.
"""
from typing import Optional, Annotated
import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError

from src.bethemc.auth.models import UserInDB
from src.bethemc.auth.service import (
    verify_token,
    get_user_by_email,
    verify_password
)
from src.bethemc.database import mongodb
from src.bethemc.config import settings

# Bearer token scheme
security = HTTPBearer(auto_error=False)

def get_token(authorization: str = Depends(security)) -> Optional[str]:
    """Extract the token from the Authorization header.
    
    Args:
        authorization: The Authorization header value
        
    Returns:
        The token string if present, None otherwise
    """
    if authorization is None:
        return None
    return authorization.credentials


async def get_current_user(token: str = Depends(get_token)) -> UserInDB:
    """
    Dependency to get the current authenticated user.
    
    Args:
        token: JWT access token from Authorization header
        
    Returns:
        UserInDB: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # Verify the access token
        token_data = verify_token(token, token_type="access")
        
        # Get the user from the database by email (which is stored in username field)
        user = await get_user_by_email(email=token_data.username)  # Changed token_data.email to token_data.username
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check if user is disabled
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except JWTError as je:
        # Handle JWT-specific errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(je)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException as he:
        # Re-raise HTTP exceptions with original status code and detail
        raise he
    except Exception as e:
        # Log the unexpected error for debugging
        import logging
        logging.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while validating credentials",
        )


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    """
    Dependency to get the current active user.
    
    This is a convenience function that's now mostly redundant since get_current_user
    already checks for disabled users. Kept for backward compatibility.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        UserInDB: The authenticated and active user
        
    Raises:
        HTTPException: If the user is disabled
    """
    # Note: The check for disabled users is now in get_current_user
    return current_user



async def get_optional_user(
    token: Optional[str] = Depends(get_token)
) -> Optional[UserInDB]:
    """
    Get the current user if authenticated, otherwise return None.
    
    This is useful for endpoints that have optional authentication.
    
    Args:
        token: Optional JWT token from Authorization header
        
    Returns:
        UserInDB if authenticated, None otherwise
    """
    if not token:
        return None
        
    try:
        # Verify the token without checking the user's active status
        token_data = verify_token(token, token_type="access")
        if not token_data:
            return None
            
        # Get the user without raising exceptions
        user = await get_user_by_email(email=token_data.email)
        return user if user and not user.disabled else None
        
    except (JWTError, HTTPException):
        # Token is invalid or expired
        return None
    except Exception as e:
        # Log unexpected errors but don't fail the request
        import logging
        logging.error(f"Error in get_optional_user: {str(e)}")
        return None


# Type aliases for better type hints and dependency injection

# For endpoints that require authentication
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]

# For endpoints with optional authentication
OptionalUser = Annotated[Optional[UserInDB], Depends(get_optional_user)]

# For endpoints that need raw token access
TokenDependency = Annotated[str, Depends(get_token)]
