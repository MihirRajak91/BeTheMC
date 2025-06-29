"""
Authentication service module.

This module contains the core authentication logic for the application.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.bethemc.auth.models import TokenData, UserInDB, UserCreate
from src.bethemc.config import settings
from src.bethemc.database import mongodb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def create_tokens(email: str) -> dict:
    """
    Create both access and refresh tokens.
    
    Args:
        email: User's email address to include in the token
        
    Returns:
        dict: Dictionary containing access_token, refresh_token, and token_type
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = jwt.encode(
        {
            "sub": email,  # Using email as the subject
            "type": "access",
            "exp": datetime.utcnow() + access_token_expires
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    refresh_token = jwt.encode(
        {
            "sub": email,  # Using email as the subject
            "type": "refresh",
            "exp": datetime.utcnow() + refresh_token_expires
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get a user by email address.
    
    Args:
        email: User's email address
        
    Returns:
        UserInDB if found, None otherwise
    """
    user_data = await mongodb.db.users.find_one({"email": email.lower()})  # Case-insensitive match
    if not user_data:
        return None
        
    # Ensure all required fields are present
    user_data["id"] = str(user_data["_id"])  # Convert ObjectId to string
    
    # Set default values for missing datetime fields
    now = datetime.utcnow()
    if "created_at" not in user_data:
        user_data["created_at"] = now
    if "updated_at" not in user_data:
        user_data["updated_at"] = now
        
    # Update the document in the database if it was missing fields
    if "_id" in user_data and ("created_at" not in user_data or "updated_at" not in user_data):
        await mongodb.db.users.update_one(
            {"_id": user_data["_id"]},
            {"$set": {
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"]
            }}
        )
        
    return UserInDB(**user_data)

# Keep for backward compatibility, but mark as deprecated
async def get_user(username: str) -> Optional[UserInDB]:
    """Get a user by username (deprecated, use get_user_by_email instead)."""
    return await get_user_by_email(username)


async def create_user(user_data: UserCreate) -> UserInDB:
    """
    Create a new user with the given data.
    
    Args:
        user_data: User creation data including email and password
        
    Returns:
        UserInDB: The created user with hashed password
        
    Raises:
        HTTPException: If user creation fails
    """
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    now = datetime.utcnow()
    
    # Prepare user document
    user_dict = user_data.dict(exclude={"password"})
    user_dict.update({
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now,
        "disabled": False,
    })
    
    # Insert the new user
    result = await mongodb.db.users.insert_one(user_dict)
    
    # Get the created user
    created_user = await get_user_by_email(user_data.email)
    if not created_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create user"
        )
    return created_user


async def get_all_users(skip: int = 0, limit: int = 100) -> list[UserInDB]:
    """
    Get all users with pagination.
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return
        
    Returns:
        List of UserInDB objects
    """
    users = []
    try:
        async for user_data in mongodb.db.users.find().skip(skip).limit(limit):
            try:
                # Ensure all required fields are present
                user_data["id"] = str(user_data["_id"])
                
                # Set default values for missing fields
                now = datetime.utcnow()
                if "created_at" not in user_data:
                    user_data["created_at"] = now
                if "updated_at" not in user_data:
                    user_data["updated_at"] = now
                if "disabled" not in user_data:
                    user_data["disabled"] = False
                if "full_name" not in user_data:
                    user_data["full_name"] = None
                    
                users.append(UserInDB(**user_data))
                
            except Exception as e:
                logging.error(f"Error processing user {user_data.get('_id')}: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )
        
    return users


async def delete_user(user_email: str, current_user_email: str) -> bool:
    """
    Delete a user by email.
    
    Args:
        user_email: Email of the user to delete
        current_user_email: Email of the user making the request (cannot delete self)
        
    Returns:
        bool: True if user was deleted, False if not found
        
    Raises:
        HTTPException: If trying to delete self or other validation fails
    """
    # Prevent users from deleting themselves
    if user_email.lower() == current_user_email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Check if user exists
    user = await get_user_by_email(user_email)
    if not user:
        return False
    
    # Delete the user by email (case-insensitive match)
    result = await mongodb.db.users.delete_one({"email": {"$regex": f"^{user_email}$", "$options": "i"}})
    return result.deleted_count > 0


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User's email address
        password: Plain text password
        
    Returns:
        UserInDB if authentication successful, None otherwise
    """
    user = await get_user_by_email(email)
    if not user:
        # Hash a dummy password to prevent timing attacks
        verify_password("dummy_password", "$2b$12$...")
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """
    Verify a JWT token and return the token data.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        logger.info(f"Decoding token with type: {token_type}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Decoded payload: {payload}")
        
        email: str = payload.get("sub")  # Email is stored in the 'sub' claim
        token_type_from_payload: str = payload.get("type")
        
        logger.info(f"Token type from payload: {token_type_from_payload}, expected: {token_type}")
        logger.info(f"Email from token: {email}")
        
        if not email:
            logger.error("No email (sub) found in token")
            raise JWTError("No email in token")
            
        if token_type_from_payload != token_type:
            logger.error(f"Token type mismatch. Expected {token_type}, got {token_type_from_payload}")
            raise JWTError(f"Invalid token type. Expected {token_type}, got {token_type_from_payload}")
            
        # Create TokenData with the correct field names
        token_data = TokenData(
            username=email,  # This will be stored in the 'username' field
            exp=payload["exp"],
            type=token_type_from_payload
        )
        logger.info(f"Token verification successful for user: {email}")
        return token_data
        
    except JWTError as e:
        error_msg = f"JWT Error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=401,
            detail=error_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        error_msg = f"Unexpected error during token verification: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=401,
            detail=error_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )
