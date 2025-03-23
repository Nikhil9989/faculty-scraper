# Faculty Matcher

A comprehensive web application for scraping faculty information from top AI/ML universities, matching student resumes with faculty profiles based on research interests, and providing a user-friendly API for accessing this functionality.

## Overview

This project aims to help students find potential research advisors by matching their resumes with faculty profiles from leading AI/ML institutions. The system provides:

- **Faculty Data Collection**: Web scraping of faculty profiles from university websites
- **Resume Parsing**: Extraction of relevant information from student resumes
- **Smart Matching Algorithm**: NLP-based compatibility scoring between students and faculty
- **API Access**: RESTful endpoints for accessing all functionality
- **Database Storage**: Structured storage of faculty and student information

## Components

The application is divided into several modules:

1. **Faculty Scraper**: Collects faculty information from university websites
2. **Resume Parser**: Extracts information from PDF resumes
3. **Resume-Faculty Matcher**: Matches student profiles with faculty using NLP
4. **Faculty API**: RESTful API for accessing the system
5. **Database**: PostgreSQL storage for all collected data

## Features

- Scraping of Stanford CS faculty profiles (extensible to other universities)
- NLP-based resume parsing for education, research interests, and publications
- Advanced matching using TF-IDF, BERT, and spaCy similarity
- RESTful API with JWT authentication and rate limiting
- Docker containerization for easy deployment
- PostgreSQL database integration

## Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper

# Start the application using Docker Compose
docker-compose up -d
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper

# Install dependencies
pip install -r requirements.txt

# Download required NLP models
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m nltk.downloader punkt stopwords

# Set up the database
python main.py setup-db

# Start the services
python main.py start-all
```

## Usage

### Command Line Interface

The application provides a command-line interface for various functions:

```bash
# Scrape faculty data
python main.py scrape

# Parse a resume
python main.py parse-resume path/to/resume.pdf

# Match a parsed resume with faculty
python main.py match path/to/parsed_resume.json

# Start API server
python main.py serve

# Start all services
python main.py start-all
```

### API Endpoints

The application exposes several API endpoints:

- **Faculty API** (port 8000):
  - `/faculty/search` - Search for faculty based on criteria
  - `/faculty/{id}` - Get details for a specific faculty member
  - `/resume/upload` - Upload a resume for processing
  - `/match` - Match a resume with faculty profiles

- **Resume Parser API** (port 5000):
  - `/upload` - Upload a resume
  - `/parse` - Parse a previously uploaded resume
  - `/parse-upload` - Upload and parse a resume in one step

## Database Schema

The PostgreSQL database includes tables for:

- Universities
- Departments
- Faculty members
- Research interests
- Publications

## License

MIT
