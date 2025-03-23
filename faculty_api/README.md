# Faculty Matching API

A FastAPI service that provides endpoints for faculty search, resume upload, and compatibility scoring with JWT authentication and rate limiting.

## Overview

This API allows authorized users to:
- Search for faculty members based on various criteria
- Upload and parse resume documents (PDF and DOCX formats)
- Match student resumes with faculty profiles to find compatible research advisors

## Authentication

The API uses JWT (JSON Web Token) authentication to secure endpoints:

- All endpoints except the health check require authentication
- Users can obtain an access token by providing valid credentials
- Admin-only endpoints are restricted to users with the 'admin' role
- Default admin credentials: admin@example.com / adminpassword (change in production)

## Rate Limiting

To prevent API abuse and ensure fair usage, the API implements rate limiting:

- All endpoints have default rate limits of 60 requests per minute per user
- Different endpoints have customized limits based on their resource intensity:
  - `/faculty/search`: 30 requests per minute
  - `/resume/upload`: 10 requests per minute
  - `/resume/parse`: 20 requests per minute
  - `/match`: 15 requests per minute (resource-intensive operation)
- Rate limits are applied per user for authenticated requests and per IP address for anonymous requests
- When rate limits are exceeded, the API returns a 429 (Too Many Requests) status code with a Retry-After header
- Rate limiting uses Redis as a backend for distributed rate tracking (falls back to memory storage if Redis is unavailable)

Rate limits can be configured via environment variables:
```
DEFAULT_RATE_LIMIT=60/minute
FACULTY_SEARCH_LIMIT=30/minute
RESUME_UPLOAD_LIMIT=10/minute
RESUME_PARSE_LIMIT=20/minute
MATCH_RATE_LIMIT=15/minute
```

## API Endpoints

### Public Endpoints

```
GET /health
```
Returns the current status of the API.

```
POST /token
```
Obtain a JWT access token for authentication.

### Protected Endpoints (require authentication)

```
GET /users/me
```
Get information about the currently authenticated user.

```
POST /faculty/search
```
Search for faculty members based on keywords, university, department, or research areas.

```
GET /faculty/{faculty_id}
```
Get detailed information about a specific faculty member.

```
POST /resume/upload
```
Upload a resume file (PDF or DOCX).

```
POST /resume/parse
```
Parse a previously uploaded resume to extract structured data.

```
POST /match
```
Match resume data with faculty profiles and return compatibility scores.

### Admin-Only Endpoints

```
POST /users
```
Register a new user (admin only).

```
POST /faculty
```
Add a new faculty member to the database (admin only).

## Example Usage

### Authentication

```bash
# Obtain a JWT token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=adminpassword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Faculty Search (with authentication)

```bash
curl -X POST "http://localhost:8000/faculty/search" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"keywords": "machine learning", "university": "Stanford"}'
```

### Resume Upload (with authentication)

```bash
curl -X POST "http://localhost:8000/resume/upload" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@/path/to/resume.pdf"
```

## Rate Limit Exceeded Response

When a rate limit is exceeded, the API will respond with:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Please try again later.",
  "limit": 60,
  "reset_after": 60
}
```

## Installation and Setup

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper/faculty_api

# Install dependencies
pip install -r requirements.txt

# Optional: Start Redis for rate limiting (or use Docker)
# docker run -d -p 6379:6379 redis:alpine

# Set environment variables (optional)
export REDIS_HOST=localhost
export REDIS_PORT=6379
export DEFAULT_RATE_LIMIT=60/minute

# Run the API
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000), and the interactive documentation (Swagger UI) at [http://localhost:8000/docs](http://localhost:8000/docs).

## Security Notes

- In production, use a secure randomly generated SECRET_KEY for JWT signing
- Store the SECRET_KEY as an environment variable, not in code
- Set restrictive CORS policies for production use
- Use HTTPS in production
- Consider setting shorter token expiration times for sensitive operations
- Ensure Redis is properly secured if used for rate limiting

## Dependencies

- FastAPI: Web framework for the API
- Uvicorn: ASGI server for running FastAPI
- Pydantic: Data validation and settings management
- Python-jose: JWT token generation and validation
- Passlib & bcrypt: Password hashing and verification
- Python-multipart: For handling file uploads
- Redis: Backend for distributed rate limiting
- slowapi: Rate limiting implementation for FastAPI

## Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- Integration with the resume parser module
- Integration with the resume-faculty matcher module
- Deployment configurations
