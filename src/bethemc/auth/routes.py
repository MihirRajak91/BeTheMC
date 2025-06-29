"""
Authentication routes for the application.

This module contains the API endpoints for user authentication.
"""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.bethemc.auth.models import Token, UserInDB, UserCreate, UserResponse
from src.bethemc.auth.dependencies import (
    CurrentUser,
    authenticate_user_form,
    get_current_active_user,
)
from src.bethemc.auth.service import (
    create_access_token,
    create_user as create_user_service,
    get_user_by_email,
)
from src.bethemc.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate_user_form(form_data)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user).dict(),
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate) -> UserInDB:
    """
    Create a new user account.
    """
    # Check if username already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create the user
    user = await create_user_service(user_data)
    return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: CurrentUser) -> UserInDB:
    """
    Get current user information.
    """
    return current_user
