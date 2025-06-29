"""
Authentication service module.

This module contains the core authentication logic for the application.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.bethemc.auth.models import TokenData, UserInDB, UserCreate
from src.bethemc.config import settings
from src.bethemc.database import mongodb

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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user(username: str) -> Optional[UserInDB]:
    """Get a user by username."""
    user_data = await mongodb.db.users.find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)
    return None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    user_data = await mongodb.db.users.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None


async def create_user(user_data: UserCreate) -> UserInDB:
    """Create a new user."""
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    
    result = await mongodb.db.users.insert_one(user_dict)
    created_user = await get_user(user_data.username)
    return created_user


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user with username and password."""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def verify_token(token: str) -> TokenData:
    """Verify a JWT token and return the token data."""
    credentials_exception = ValueError("Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError as e:
        raise credentials_exception from e
    return token_data
