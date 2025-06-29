# Authentication System Documentation

## Overview
The BeTheMC API uses JWT (JSON Web Tokens) for authentication. This document explains how the authentication system works and how to use it.

## Table of Contents
- [Authentication Flow](#authentication-flow)
- [Endpoints](#endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Environment Variables](#environment-variables)

## Authentication Flow

1. **Registration**: User creates an account with email and password
2. **Login**: User authenticates and receives a JWT token
3. **Access Protected Routes**: Token is sent in the `Authorization` header for subsequent requests
4. **Token Refresh**: When the token expires, user logs in again to get a new token

## Endpoints

### 1. Register a New User

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "example_user"
}
```

**Response (201 Created)**:
```json
{
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "example_user",
    "is_active": true,
    "created_at": "2025-06-29T09:45:00Z"
}
```

### 2. Login (Get Access Token)

**Endpoint**: `POST /auth/token`

**Form Data**:
- `username`: User's email or username
- `password`: User's password

**Response (200 OK)**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 3. Get Current User

**Endpoint**: `GET /auth/me`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "example_user",
    "is_active": true,
    "created_at": "2025-06-29T09:45:00Z"
}
```

## Request/Response Examples

### Using cURL

**Register a new user**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123","username":"example_user"}'
```

**Get access token**:
```bash
curl -X POST http://localhost:8000/auth/token \
  -d "username=user@example.com" \
  -d "password=securepassword123" \
  -d "grant_type=password"
```

**Access protected endpoint**:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication credentials
- `403 Forbidden`: User doesn't have permission to access the resource
- `404 Not Found`: Resource not found
- `409 Conflict`: Email or username already exists
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

Example error response:
```json
{
    "detail": "Incorrect email or password"
}
```

## Security Considerations

1. **Password Security**:
   - Passwords are hashed using bcrypt before storage
   - Minimum password length is 8 characters
   - Common passwords are rejected

2. **Token Security**:
   - JWT tokens are signed using HS256 algorithm
   - Tokens expire after a configurable time (default: 30 minutes)
   - Tokens must be sent in the `Authorization: Bearer` header

3. **HTTPS**:
   - Always use HTTPS in production
   - HSTS is recommended

## Environment Variables

The following environment variables are used for authentication:

```bash
# Required
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=bethemc
SECRET_KEY=your-secret-key-here

# Optional (with defaults)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing Authentication

1. Start the server:
   ```bash
   uvicorn bethemc.api.app:app --reload
   ```

2. Register a new user using the `/auth/register` endpoint
3. Get an access token using the `/auth/token` endpoint
4. Use the token to access protected endpoints

## Troubleshooting

- **Invalid credentials**: Double-check the email/username and password
- **Token expired**: Get a new token by logging in again
- **Connection issues**: Ensure MongoDB is running and accessible
- **CORS issues**: Verify the CORS settings in the API configuration

For additional help, please refer to the API documentation at `/docs` when the server is running.
