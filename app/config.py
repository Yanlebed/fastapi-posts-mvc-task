import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings and configuration variables.
    Contains all the environment variables and settings for the application.
    """
    PROJECT_NAME: str = "FastAPI Posts MVC App"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://username:password@localhost/fastapi_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_for_jwt")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()