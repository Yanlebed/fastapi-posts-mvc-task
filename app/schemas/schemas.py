from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """
    Base Pydantic model for User data.
    Contains fields common to all user-related schemas.

    Attributes:
        email (EmailStr): User's email address with email validation
    """
    email: EmailStr = Field(..., description="User email address")

    @validator('email')
    def email_must_be_valid(cls, v):
        """
        Validates that the email is in a proper format.

        Args:
            v (str): The email to validate

        Returns:
            str: The validated email if valid

        Raises:
            ValueError: If email format is invalid
        """
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError('Invalid email format')
        return v


class UserCreate(UserBase):
    """
    Pydantic model for user creation (signup).
    Extends UserBase with password field.

    Attributes:
        password (str): User password with length validation
    """
    password: str = Field(..., min_length=8, max_length=100,
                          description="User password (must contain at least one digit, one uppercase letter, and one special character)")

    @validator('password')
    def password_must_be_strong(cls, v):
        """
        Validates that the password meets strength requirements.

        Args:
            v (str): The password to validate

        Returns:
            str: The validated password if valid

        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        # Check for special characters
        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/\\"
        if not any(char in special_chars for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """
    Pydantic model for user login.
    Contains email and password fields for authentication.

    Attributes:
        email (EmailStr): User's email address with email validation
        password (str): User password
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Pydantic model for authentication token.

    Attributes:
        access_token (str): JWT access token
        token_type (str): Type of token (typically "bearer")
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Pydantic model for token payload data.

    Attributes:
        email (Optional[str]): Email from the token payload
        exp (Optional[datetime]): Token expiration time
    """
    email: Optional[str] = None
    exp: Optional[datetime] = None


class PostBase(BaseModel):
    """
    Base Pydantic model for Post data.
    Contains fields common to all post-related schemas.

    Attributes:
        text (str): Content of the post with length validation
    """
    text: str = Field(..., min_length=1, max_length=1000000, description="Post content")

    @validator('text')
    def validate_post_size(cls, v):
        """
        Validates that the post doesn't exceed size limit (1MB).

        Args:
            v (str): The post text to validate

        Returns:
            str: The validated post text if valid

        Raises:
            ValueError: If post exceeds size limit
        """
        # Check if post size exceeds 1MB (approximately)
        if len(v.encode('utf-8')) > 1000000:  # 1MB in bytes
            raise ValueError('Post size exceeds 1MB limit')
        return v


class PostCreate(PostBase):
    """
    Pydantic model for post creation.
    Extends PostBase with additional fields for post creation.
    """
    pass


class Post(PostBase):
    """
    Pydantic model for post response.
    Extends PostBase with additional fields for the complete post representation.

    Attributes:
        id (int): Post ID
        user_id (int): ID of the user who created the post
        created_at (datetime): Timestamp of when the post was created
    """
    id: int
    user_id: int
    created_at: datetime

    class Config:
        """
        Configuration for the Post model.
        """
        orm_mode = True


class PostDelete(BaseModel):
    """
    Pydantic model for post deletion.

    Attributes:
        post_id (int): ID of the post to be deleted
    """
    post_id: int = Field(..., gt=0, description="ID of the post to delete")