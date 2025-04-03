from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from passlib.context import CryptContext

from app.models.models import User, Post

# Create a password context directly in repositories to avoid circular import
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


class UserRepository:
    """
    Repository class for User entity.
    Handles database operations related to User model.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def create_user(self, email: str, password: str) -> User:
        """
        Creates a new user with the provided email and password.

        Args:
            email (str): User's email address
            password (str): User's password (will be hashed)

        Returns:
            User: The created user object

        Raises:
            SQLAlchemyError: If there's an error creating the user
        """
        try:
            # Hash the password before storing it
            hashed_password = get_password_hash(password)

            # Create a new user object
            db_user = User(email=email, hashed_password=hashed_password)

            # Add and commit to the database
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user by their email address.

        Args:
            email (str): Email address to search for

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): User ID to search for

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()


class PostRepository:
    """
    Repository class for Post entity.
    Handles database operations related to Post model.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def create_post(self, user_id: int, text: str) -> Post:
        """
        Creates a new post for the specified user.

        Args:
            user_id (int): ID of the user creating the post
            text (str): Content of the post

        Returns:
            Post: The created post object

        Raises:
            SQLAlchemyError: If there's an error creating the post
        """
        try:
            # Create a new post object
            db_post = Post(text=text, user_id=user_id)

            # Add and commit to the database
            self.db.add(db_post)
            self.db.commit()
            self.db.refresh(db_post)

            return db_post
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_posts_by_user_id(self, user_id: int) -> List[Post]:
        """
        Retrieves all posts for a specific user.

        Args:
            user_id (int): ID of the user whose posts to retrieve

        Returns:
            List[Post]: List of posts belonging to the user
        """
        return self.db.query(Post).filter(Post.user_id == user_id).all()

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """
        Retrieves a post by its ID.

        Args:
            post_id (int): Post ID to search for

        Returns:
            Optional[Post]: The post if found, None otherwise
        """
        return self.db.query(Post).filter(Post.id == post_id).first()

    def delete_post(self, post_id: int, user_id: int) -> bool:
        """
        Deletes a post if it belongs to the specified user.

        Args:
            post_id (int): ID of the post to delete
            user_id (int): ID of the user who owns the post

        Returns:
            bool: True if the post was deleted, False otherwise

        Raises:
            SQLAlchemyError: If there's an error deleting the post
        """
        try:
            # Get the post and check if it belongs to the user
            post = self.db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()

            if not post:
                return False

            # Delete the post and commit
            self.db.delete(post)
            self.db.commit()

            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e