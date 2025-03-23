# Resume Parser API

A Flask-based API for uploading and parsing student resumes to extract relevant information for faculty matching.

## Overview

This API allows users to:
- Upload resume files (PDF)
- Parse resumes to extract key information (name, education, research interests)
- Return structured data that can be used for matching with faculty profiles

## API Endpoints

### Health Check
```
GET /health
```
Returns the current status of the API.

### Upload Resume
```
POST /upload
```
Upload a resume file (PDF).

**Request:**
- Form data with a 'file' field containing the resume PDF

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "filename": "resume.pdf",
  "file_path": "uploads/resume.pdf"
}
```

### Parse Resume
```
POST /parse
```
Parse a previously uploaded resume.

**Request:**
```json
{
  "filename": "resume.pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "John Doe",
    "education": [
      {
        "degree": "PhD",
        "field": "Computer Science",
        "institution": "Stanford University",
        "year": 2020
      }
    ],
    "research_interests": [
      "Machine Learning",
      "Natural Language Processing",
      "Computer Vision"
    ]
  }
}
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper/resume_parser

# Install dependencies
pip install -r requirements.txt

# Run the API
python app.py
```

## Dependencies

- Flask: Web framework for the API
- Werkzeug: Utility library for Flask
- PyMuPDF (coming soon): For PDF parsing

## Future Enhancements

- Support for DOCX files
- Improved parsing accuracy
- Integration with faculty matching algorithm
