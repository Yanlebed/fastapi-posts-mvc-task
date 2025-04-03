from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time

from app.models.models import Base
from app.database import engine
from app.controllers.controllers import auth_router, post_router
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI MVC application with JWT authentication",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication operations"},
        {"name": "Posts", "description": "Post management operations"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add request processing time to response headers.

    Args:
        request (Request): FastAPI request object
        call_next (Callable): Next middleware function

    Returns:
        Response: FastAPI response object
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Add routers
app.include_router(auth_router, prefix="/api")
app.include_router(post_router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        Dict: Welcome message
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
    }


# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint to verify API status.

    Returns:
        Dict: Status information
    """
    return {"status": "healthy"}


# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)