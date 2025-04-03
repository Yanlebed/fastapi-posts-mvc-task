from fastapi import HTTPException, status
from typing import List, Dict, Any
import time

from app.repositories.repositories import UserRepository, PostRepository
from app.middleware.auth import verify_password, create_access_token
from app.schemas.schemas import PostCreate, PostDelete


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def signup(self, email: str, password: str) -> Dict[str, str]:
        # Check if the user already exists
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create the new user
        user = self.user_repository.create_user(email, password)

        # Generate an access token
        access_token = create_access_token(data={"sub": user.email})

        return {"access_token": access_token, "token_type": "bearer"}

    def login(self, email: str, password: str) -> Dict[str, str]:
        # Get the user by email
        user = self.user_repository.get_user_by_email(email)

        # Check if the user exists and the password is correct
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate an access token
        access_token = create_access_token(data={"sub": user.email})

        return {"access_token": access_token, "token_type": "bearer"}


class PostService:

    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
        self.cache = {}  # Simple in-memory cache

    def create_post(self, user_id: int, post_data: PostCreate) -> Dict[str, int]:
        # Create the post
        post = self.post_repository.create_post(user_id, post_data.text)

        # Invalidate the cache for this user
        if str(user_id) in self.cache:
            del self.cache[str(user_id)]

        return {"post_id": post.id}

    def get_posts(self, user_id: int) -> List[Dict[str, Any]]:
        # Check if the posts are in the cache and not expired
        cache_key = str(user_id)
        current_time = time.time()

        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]

            # Check if the cache is still valid (less than 5 minutes old)
            if current_time - cache_time < 300:  # 300 seconds = 5 minutes
                return cache_data

        # If not in cache or cache expired, fetch from database
        posts = self.post_repository.get_posts_by_user_id(user_id)

        # Convert posts to dictionaries
        result = [
            {
                "id": post.id,
                "text": post.text,
                "created_at": post.created_at
            }
            for post in posts
        ]

        # Update the cache
        self.cache[cache_key] = (result, current_time)

        return result

    def delete_post(self, user_id: int, post_data: PostDelete) -> Dict[str, bool]:
        # Delete the post
        deleted = self.post_repository.delete_post(post_data.post_id, user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or doesn't belong to you"
            )

        # Invalidate the cache for this user
        if str(user_id) in self.cache:
            del self.cache[str(user_id)]

        return {"success": True}