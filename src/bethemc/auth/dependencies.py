"""
Authentication dependencies for FastAPI routes.

This module provides dependencies for handling authentication in API routes.
"""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.bethemc.auth.models import TokenData, UserInDB, UserCreate
from src.bethemc.auth.service import (
    verify_token,
    get_user,
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from src.bethemc.database import mongodb
from datetime import timedelta

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items.",
    },
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = verify_token(token)
        user = await get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        raise credentials_exception from e


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    """Dependency to get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def authenticate_user_form(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> UserInDB:
    """Authenticate a user with username and password from form data."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[UserInDB]:
    """Get the current user if authenticated, otherwise return None."""
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


# Type aliases for better type hints
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
OptionalUser = Annotated[Optional[UserInDB], Depends(get_optional_user)]
TokenDependency = Annotated[str, Depends(oauth2_scheme)]
