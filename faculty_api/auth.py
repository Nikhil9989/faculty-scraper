"""
Authentication module for Faculty API.

This module provides JWT-based authentication functionality.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")  # In production, use a secure environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
USER_DB_FILE = "data/users.json"

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define user models
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"  # user, admin

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# User database functions
def get_user_db():
    """Get user database from file."""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user database: {e}")
    
    # If file doesn't exist or there's an error, return empty DB
    return []

def save_user_db(users):
    """Save user database to file."""
    try:
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving user database: {e}")

def get_user(email: str):
    """Get user from database by email."""
    users = get_user_db()
    for user in users:
        if user["email"] == email:
            return UserInDB(**user)
    return None

def create_user(user: UserCreate):
    """Create a new user in the database."""
    users = get_user_db()
    
    # Check if user already exists
    if any(u["email"] == user.email for u in users):
        return False
    
    # Create new user with hashed password
    user_id = str(len(users) + 1)  # Simple ID generation
    hashed_password = pwd_context.hash(user.password)
    
    user_dict = user.dict()
    user_dict.pop("password")
    user_dict["id"] = user_id
    user_dict["hashed_password"] = hashed_password
    user_dict["disabled"] = False
    
    users.append(user_dict)
    save_user_db(users)
    
    return UserInDB(**user_dict)

# Password and token functions
def verify_password(plain_password, hashed_password):
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password."""
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role", "user")
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = get_user(token_data.email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Verify user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def is_admin(user: User):
    """Check if user has admin role."""
    return user.role == "admin"

# Create a dependency for admin-only endpoints
async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """Verify user is an admin."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user

# Initialize admin user if none exists
def init_admin():
    """Initialize admin user if no users exist."""
    users = get_user_db()
    if not users:
        admin_user = UserCreate(
            email="admin@example.com",
            password="adminpassword",  # In production, use a secure password
            full_name="Admin User",
            role="admin"
        )
        create_user(admin_user)
        logger.info("Created initial admin user")

# Initialize admin user on module import
init_admin()
