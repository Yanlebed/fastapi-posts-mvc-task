from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, List, Any

# Import models and schemas first
from app.models.models import User
from app.schemas.schemas import UserCreate, PostCreate, PostDelete, Token
from app.database import get_db

# Then import auth dependencies
from app.middleware.auth import get_current_user

# Finally import repositories and services
from app.repositories.repositories import UserRepository, PostRepository
from app.services.services import UserService, PostService

# Create routers
auth_router = APIRouter(tags=["Authentication"])
post_router = APIRouter(tags=["Posts"])


@auth_router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Endpoint for user registration.

    Args:
        user_data (UserCreate): User signup data including email and password
        db (Session): Database session dependency

    Returns:
        Dict[str, str]: Dictionary containing the access token and token type
    """
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    return user_service.signup(user_data.email, user_data.password)


@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Endpoint for user authentication.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data with username and password
        db (Session): Database session dependency

    Returns:
        Dict[str, str]: Dictionary containing the access token and token type
    """
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    # OAuth2 form uses 'username' field, but our system uses 'email'
    return user_service.login(form_data.username, form_data.password)


@post_router.post("/posts", response_model=Dict[str, int])
async def add_post(
        post_data: PostCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Dict[str, int]:
    """
    Endpoint for creating a new post.
    Requires authentication.

    Args:
        post_data (PostCreate): Post creation data including text
        current_user (User): Current authenticated user dependency
        db (Session): Database session dependency

    Returns:
        Dict[str, int]: Dictionary containing the post ID
    """
    post_repository = PostRepository(db)
    post_service = PostService(post_repository)

    return post_service.create_post(current_user.id, post_data)


@post_router.get("/posts", response_model=List[Dict[str, Any]])
async def get_posts(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Endpoint for retrieving all posts for the current user.
    Requires authentication.
    Uses caching to improve performance.

    Args:
        current_user (User): Current authenticated user dependency
        db (Session): Database session dependency

    Returns:
        List[Dict[str, Any]]: List of posts with their details
    """
    post_repository = PostRepository(db)
    post_service = PostService(post_repository)

    return post_service.get_posts(current_user.id)


@post_router.delete("/posts", response_model=Dict[str, bool])
async def delete_post(
        post_data: PostDelete,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Endpoint for deleting a post.
    Requires authentication.

    Args:
        post_data (PostDelete): Post deletion data including post_id
        current_user (User): Current authenticated user dependency
        db (Session): Database session dependency

    Returns:
        Dict[str, bool]: Dictionary indicating success or failure
    """
    post_repository = PostRepository(db)
    post_service = PostService(post_repository)

    return post_service.delete_post(current_user.id, post_data)