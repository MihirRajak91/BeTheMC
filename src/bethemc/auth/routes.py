"""
Authentication routes for the application.

This module contains the API endpoints for user authentication, including:
- User registration and login
- Token refresh
- User management
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging

# Third-party imports
from fastapi import (
    APIRouter, 
    Depends, 
    Form, 
    HTTPException, 
    Path, 
    Query, 
    Request, 
    status
)
from fastapi.security import HTTPBearer
from jose import JWTError

# Application imports
from src.bethemc.auth.models import (
    Token, 
    UserInDB, 
    UserCreate, 
    UserResponse, 
    RefreshTokenRequest
)
from src.bethemc.auth.dependencies import (
    CurrentUser,
    get_current_active_user,
)
from src.bethemc.auth.service import (
    create_tokens,
    create_user as create_user_service,
    get_user_by_email,
    get_all_users,
    delete_user as delete_user_service,
    verify_token,
    verify_password
)
from src.bethemc.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Security scheme for Bearer tokens
security = HTTPBearer(auto_error=False)

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
) -> Token:
    """
    Login and get access & refresh tokens using email and password.
    
    This endpoint authenticates a user with their email and password, and returns
    a pair of JWT tokens (access and refresh) if successful.
    
    Args:
        email: The user's email address
        password: The user's password (plaintext, will be verified against the hash)
        
    Returns:
        Token: Object containing access_token, refresh_token, and token_type
        
    Raises:
        HTTPException: If authentication fails (401) or other errors occur (500)
    """
    try:
        # Log the login attempt (without logging the actual password)
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Login attempt for email: {email} from {client_host}")
        
        # Find user by email (case-insensitive)
        user = await get_user_by_email(email)
        
        # Verify user exists and password is correct
        if not user:
            logger.warning(f"Login failed: User not found - {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
            
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password for user - {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
            
        # Check if user account is disabled
        if user.disabled:
            logger.warning(f"Login failed: Account disabled - {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
            
        # Generate tokens
        logger.info(f"Login successful for user: {email}")
        return create_tokens(user.email)
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 401, 403) with their original status codes
        raise
        
    except Exception as e:
        # Log the full error but return a generic message to the client
        logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password (min 8 characters)"),
    full_name: str = Form(None, description="User's full name (optional)")
) -> UserResponse:
    """
    Register a new user with email and password.
    
    This endpoint creates a new user account with the provided information.
    The password will be hashed before storage.
    
    Args:
        email: User's email address (must be unique and valid email format)
        password: User's password (will be hashed, min 8 characters)
        full_name: Optional full name of the user
        
    Returns:
        UserResponse: The created user's information (without sensitive data)
        
    Raises:
        HTTPException: 
            - 400: If email is already registered or validation fails
            - 422: If input validation fails
            - 500: If an unexpected error occurs
    """
    try:
        # Log the registration attempt
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Registration attempt for email: {email} from {client_host}")
        
        # Basic input validation
        if not email or "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid email format"
            )
            
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters long"
            )
        
        # Check if user already exists (case-insensitive)
        existing_user = await get_user_by_email(email)
        if existing_user:
            logger.warning(f"Registration failed: Email already exists - {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create the user
        user_data = UserCreate(
            email=email.lower().strip(),  # Normalize email
            password=password,
            full_name=full_name.strip() if full_name else None
        )
        
        # Save the user to the database
        user = await create_user_service(user_data)
        logger.info(f"User registered successfully: {email}")
        
        # Return the created user (without sensitive data)
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions with their original status codes
        raise
        
    except Exception as e:
        # Log the full error but return a generic message to the client
        logger.error(f"Registration error for {email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest
) -> Token:
    """
    Get a new access token using a refresh token.
    
    This endpoint allows users to get a new access token using a valid refresh token.
    The refresh token should be included in the request body as JSON:
    
    ```json
    {
        "refresh_token": "your_refresh_token_here"
    }
    ```
    
    Args:
        refresh_request: The refresh token request containing the refresh token
        
    Returns:
        Token: A new access token and a new refresh token
        
    Raises:
        HTTPException: If the refresh token is invalid, expired, or the user no longer exists
    """
    try:
        # Verify the refresh token
        token_data = verify_token(refresh_request.refresh_token, token_type="refresh")
        
        # Verify the user still exists
        user = await get_user_by_email(token_data.email)
        if not user:
            logger.warning(f"Refresh token for non-existent user: {token_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        # Check if the user is disabled
        if user.disabled:
            logger.warning(f"Disabled user attempted to refresh token: {token_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
            
        # Create new tokens
        logger.info(f"Issuing new tokens for user: {token_data.email}")
        return create_tokens(user.email)
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with their original status codes
        logger.warning(f"Refresh token HTTP error: {str(http_exc.detail)}")
        raise
    except JWTError as jwt_err:
        # Handle JWT-specific errors
        logger.warning(f"JWT error during token refresh: {str(jwt_err)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    except Exception as e:
        # Log the error and return a generic message
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing the token"
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current authenticated user's information.
    
    Returns detailed information about the currently authenticated user,
    including their email, full name, and account status.
    
    Args:
        current_user: The currently authenticated user (injected by dependency)
        
    Returns:
        UserResponse: The user's information
        
    Raises:
        HTTPException: If the user is not authenticated or the token is invalid
    """
    try:
        # Return the current user's information
        return current_user
    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
):
    """
    List all users.
    
    Returns a paginated list of all users. This endpoint is public and does not require authentication.
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return (max 1000)
        
    Returns:
        List of user objects with sensitive information removed
    """
    try:
        users = await get_all_users(skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.delete("/users/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_email: str = Path(..., description="Email of the user to delete"),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Delete a user by email.
    
    Permanently deletes the specified user from the database.
    
    Args:
        user_email: Email of the user to delete
        current_user: The currently authenticated user
        
    Returns:
        None with 204 status code on success
        
    Raises:
        HTTPException: If user is not found, trying to delete self, or other error occurs
    """
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    # Delete the user
    try:
        deleted = await delete_user_service(user_email, current_user.email)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return None
        
    except HTTPException:
        # Re-raise HTTP exceptions with their original status codes
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user"
        )
