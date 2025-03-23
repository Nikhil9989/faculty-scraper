# Faculty Matching API

A FastAPI service that provides endpoints for faculty search, resume upload, and compatibility scoring.

## Overview

This API allows users to:
- Search for faculty members based on various criteria
- Upload and parse resume documents (PDF and DOCX formats)
- Match student resumes with faculty profiles to find compatible research advisors

## API Endpoints

### Health Check
```
GET /health
```
Returns the current status of the API.

### Faculty Search
```
POST /faculty/search
```
Search for faculty members based on keywords, university, department, or research areas.

**Example Request:**
```json
{
  "keywords": "machine learning",
  "university": "Stanford",
  "department": "Computer Science",
  "research_areas": ["Artificial Intelligence", "Computer Vision"]
}
```

### Faculty Details
```
GET /faculty/{faculty_id}
```
Get detailed information about a specific faculty member.

### Add Faculty
```
POST /faculty
```
Add a new faculty member to the database.

### Resume Upload
```
POST /resume/upload
```
Upload a resume file (PDF or DOCX).

### Resume Parsing
```
POST /resume/parse
```
Parse a previously uploaded resume to extract structured data.

**Example Request:**
```json
{
  "filename": "resume_123.pdf"
}
```

### Match Resume with Faculty
```
POST /match
```
Match resume data with faculty profiles and return compatibility scores.

**Example Request:**
```json
{
  "name": "John Doe",
  "research_interests": ["Machine Learning", "Computer Vision"],
  "education": [
    {
      "degree": "MS",
      "field": "Computer Science",
      "institution": "Stanford University",
      "year": 2023
    }
  ]
}
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

## Dependencies

- FastAPI: Web framework for the API
- Uvicorn: ASGI server for running FastAPI
- Pydantic: Data validation and settings management
- Python-multipart: For handling file uploads

## Future Enhancements

- Authentication and authorization
- Database integration (PostgreSQL/MongoDB)
- Integration with the resume parser module
- Integration with the resume-faculty matcher module
- API rate limiting
- Deployment configurations
