from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Optional, Any

from app.config import settings
from app.models.models import User
from app.schemas.schemas import TokenData
from app.database import get_db

# OAuth2 scheme for token authentication - set the correct tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain-text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided plain-text password matches the hashed password.

    Args:
        plain_password (str): The plain-text password to verify
        hashed_password (str): The hashed password to check against

    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token with the provided data and expiration time.

    Args:
        data (dict): The data to encode in the token
        expires_delta (Optional[timedelta]): The token expiration time

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Verifies the JWT token and returns the corresponding user.

    Args:
        token (str): The JWT token to verify
        db (Session): Database session

    Returns:
        User: The user corresponding to the token

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception

    # Check if the token is expired
    if token_data.exp:
        # Convert to naive datetime for comparison if exp is timezone-aware
        if token_data.exp.tzinfo is not None:
            expiration_time = token_data.exp.replace(tzinfo=None)
        else:
            expiration_time = token_data.exp

        if expiration_time < datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Get the user from the database directly (without using UserRepository)
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None:
        raise credentials_exception

    return user