# FastAPI MVC Application

This repository contains a FastAPI web application built following the MVC (Model-View-Controller) design pattern. The application provides user authentication functionality and allows for creating, retrieving, and deleting posts.

## Architecture

The application follows a layered architecture with a clear separation of concerns:

- **Models Layer**: SQLAlchemy models for database entities
- **Controllers Layer**: FastAPI route handlers and API endpoint definitions
- **Services Layer**: Business logic implementation
- **Repositories Layer**: Database operations and queries
- **Schemas Layer**: Pydantic models for request/response validation

## Features

- User registration and authentication with JWT tokens
- Post management (create, retrieve, delete)
- Token-based authentication for protected endpoints
- Request validation with Pydantic
- Response caching for improved performance
- Database integration with SQLAlchemy ORM
- Swagger UI integration for API testing with OAuth2 authentication

## Getting Started

### Prerequisites

- Python 3.7+
- MySQL database

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-mvc-app.git
   cd fastapi-mvc-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Alternatively, install the packages individually:
   ```
   pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart python-dotenv pymysql bcrypt email-validator cryptography
   ```

4. Set up your database (MySQL):
   
   ```sql
   CREATE DATABASE fastapi_db;
   CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON fastapi_db.* TO 'fastapi_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
   
   Then update the `.env` file:
   ```
   DATABASE_URL=mysql+pymysql://fastapi_user:your_password@localhost/fastapi_db
   SECRET_KEY=your_secret_key_for_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Running the Application

1. Start the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

2. The API will be available at `http://localhost:8000`
3. Swagger documentation is available at `http://localhost:8000/docs`

## API Endpoints

### Authentication

- **POST /api/signup**: Register a new user
  - Request body: `{ "email": "user@example.com", "password": "Password123!" }`
  - Response: `{ "access_token": "eyJ...", "token_type": "bearer" }`

- **POST /api/login**: Login with existing credentials
  - Form data: `username=user@example.com&password=Password123!`
  - Response: `{ "access_token": "eyJ...", "token_type": "bearer" }`

### Posts

- **POST /api/posts**: Create a new post (requires authentication)
  - Request body: `{ "text": "Post content" }`
  - Response: `{ "post_id": 1 }`

- **GET /api/posts**: Get all posts for the current user (requires authentication)
  - Response: `[{ "id": 1, "text": "Post content", "created_at": "2023-01-01T12:00:00" }]`

- **DELETE /api/posts**: Delete a post (requires authentication)
  - Request body: `{ "post_id": 1 }`
  - Response: `{ "success": true }`

## Testing the API

### Using Swagger UI

The easiest way to test the API is using the built-in Swagger UI at `http://localhost:8000/docs`:

1. Navigate to the Swagger UI
2. Click on the "Authorize" button at the top right
3. Enter your credentials (email as username and password)
4. Click "Authorize" and then "Close"
5. You can now test all the protected endpoints

### Using curl

You can also test the API using curl:

1. Register a new user:
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/signup' \
     -H 'Content-Type: application/json' \
     -d '{
       "email": "user@example.com",
       "password": "Password123!"
     }'
   ```

2. Login to get a token:
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=user@example.com&password=Password123!'
   ```

3. Use the returned token to create a post:
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/posts' \
     -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
     -H 'Content-Type: application/json' \
     -d '{
       "text": "This is my first post!"
     }'
   ```

4. Get all posts for the current user:
   ```bash
   curl -X 'GET' \
     'http://localhost:8000/api/posts' \
     -H 'Authorization: Bearer YOUR_TOKEN_HERE'
   ```

5. Delete a post:
   ```bash
   curl -X 'DELETE' \
     'http://localhost:8000/api/posts' \
     -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
     -H 'Content-Type: application/json' \
     -d '{
       "post_id": 1
     }'
   ```

## Password Requirements

Passwords must meet the following criteria:
- At least 8 characters long
- Contain at least one uppercase letter
- Contain at least one digit
- Contain at least one special character

## Project Structure

```
fastapi-mvc-app/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection setup
│   ├── models/           # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── models.py     # User and Post models
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py    # Request/response schemas
│   ├── controllers/      # API route handlers
│   │   ├── __init__.py
│   │   └── controllers.py # Route definitions
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   └── services.py   # User and Post services
│   ├── repositories/     # Database operations
│   │   ├── __init__.py
│   │   └── repositories.py # User and Post repositories
│   └── middleware/       # Middleware components
│       ├── __init__.py
│       └── auth.py       # Authentication middleware
├── .env                  # Environment variables
└── requirements.txt      # Project dependencies
```

## Notes

- The application uses in-memory caching for the GetPosts endpoint with a 5-minute cache duration
- Make sure to use strong passwords following the requirements
- Token-based authentication is implemented using JWT tokens
- The application validates payload size for the AddPost endpoint (limit: 1MB)
