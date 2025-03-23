# Faculty Matching API

A FastAPI service that provides endpoints for faculty search, resume upload, and compatibility scoring with JWT authentication.

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

## Installation and Setup

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper/faculty_api

# Install dependencies
pip install -r requirements.txt

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

## Dependencies

- FastAPI: Web framework for the API
- Uvicorn: ASGI server for running FastAPI
- Pydantic: Data validation and settings management
- Python-jose: JWT token generation and validation
- Passlib & bcrypt: Password hashing and verification
- Python-multipart: For handling file uploads

## Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- Integration with the resume parser module
- Integration with the resume-faculty matcher module
- API rate limiting
- Deployment configurations
