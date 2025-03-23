# Resume Parser API

A Flask-based API for uploading and parsing student resumes to extract relevant information for faculty matching.

## Overview

This API allows users to:
- Upload resume files (PDF and DOCX formats)
- Parse resumes to extract key information (name, education, research interests)
- Return structured data that can be used for matching with faculty profiles

## API Endpoints

### Health Check
```
GET /health
```
Returns the current status of the API.

### Supported Formats
```
GET /supported-formats
```
Returns the list of supported file formats for resume parsing.

### Upload Resume
```
POST /upload
```
Upload a resume file (PDF or DOCX).

**Request:**
- Form data with a 'file' field containing the resume file

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "filename": "resume.pdf",
  "file_path": "uploads/resume.pdf",
  "file_type": "pdf"
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
  },
  "file_type": "pdf"
}
```

### Parse and Upload
```
POST /parse-upload
```
Upload and parse a resume in a single API call.

**Request:**
- Form data with a 'file' field containing the resume file

**Response:**
- Same as `/parse` endpoint, but includes upload information as well

## Supported File Formats

Currently, the resume parser supports:

- PDF documents (`.pdf`)
- Microsoft Word documents (`.docx`)

## Installation

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper/resume_parser

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional but recommended)
python -m spacy download en_core_web_sm

# Run the API
python app.py
```

## Dependencies

- Flask: Web framework for the API
- Werkzeug: Utility library for Flask
- PyMuPDF: For PDF parsing
- python-docx: For DOCX parsing
- spaCy: For natural language processing and entity extraction

## Architecture

The parser uses a factory pattern to support multiple file formats:

- `ResumeParser`: Base parser implementation for PDF files
- `DocxResumeParser`: Implementation for DOCX files
- `ParserFactory`: Creates the appropriate parser based on file extension

## Future Enhancements

- Support for additional file formats (RTF, TXT, HTML)
- Improved parsing accuracy
- Integration with faculty matching algorithm
