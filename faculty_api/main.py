"""
Faculty Matching API

A FastAPI service that provides endpoints for faculty search,
resume upload, and compatibility scoring.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import logging
import uuid
import uvicorn
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Faculty Matching API",
    description="API for faculty search, resume upload, and compatibility scoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define model schemas
class ResearchInterest(BaseModel):
    name: str = Field(..., description="Name of the research interest")

class Education(BaseModel):
    degree: str = Field(..., description="Degree obtained")
    field: str = Field(..., description="Field of study")
    institution: str = Field(..., description="Institution name")
    year: Optional[int] = Field(None, description="Year completed")

class Publication(BaseModel):
    title: str = Field(..., description="Publication title")
    authors: Optional[str] = Field(None, description="Publication authors")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Publication venue")
    url: Optional[str] = Field(None, description="Publication URL")

class Faculty(BaseModel):
    faculty_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Faculty name")
    title: Optional[str] = Field(None, description="Faculty title")
    email: Optional[str] = Field(None, description="Faculty email")
    department_name: str = Field(..., description="Department name")
    university_name: str = Field(..., description="University name")
    research_interests: List[str] = Field([], description="Research interests")
    education: Optional[List[Education]] = Field(None, description="Education history")
    publications: Optional[List[Publication]] = Field(None, description="Publications")
    profile_url: Optional[str] = Field(None, description="Profile URL")

class ResumeData(BaseModel):
    name: Optional[str] = Field(None, description="Name from resume")
    research_interests: List[str] = Field([], description="Research interests from resume")
    education: Optional[List[Education]] = Field(None, description="Education from resume")
    publications: Optional[List[Publication]] = Field(None, description="Publications from resume")

class MatchResult(BaseModel):
    faculty_id: str = Field(..., description="Faculty identifier")
    name: str = Field(..., description="Faculty name")
    department: str = Field(..., description="Department name")
    university: str = Field(..., description="University name")
    interests_similarity: float = Field(..., description="Research interests similarity score")
    education_similarity: float = Field(..., description="Education similarity score")
    publications_similarity: float = Field(..., description="Publications similarity score")
    overall_score: float = Field(..., description="Overall compatibility score")

class SearchQuery(BaseModel):
    keywords: Optional[str] = Field(None, description="Search keywords")
    university: Optional[str] = Field(None, description="Filter by university")
    department: Optional[str] = Field(None, description="Filter by department")
    research_areas: Optional[List[str]] = Field(None, description="Filter by research areas")

# Create data directories
UPLOAD_DIR = "uploads"
FACULTY_DATA_FILE = "data/faculty_data.json"
RESUME_DATA_DIR = "data/resumes"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FACULTY_DATA_FILE), exist_ok=True)
os.makedirs(RESUME_DATA_DIR, exist_ok=True)

# Mock database (in-memory for now, replace with actual DB in production)
faculty_db = []

# Load faculty data if file exists
if os.path.exists(FACULTY_DATA_FILE):
    try:
        with open(FACULTY_DATA_FILE, "r") as f:
            faculty_db = json.load(f)
        logger.info(f"Loaded {len(faculty_db)} faculty records from {FACULTY_DATA_FILE}")
    except Exception as e:
        logger.error(f"Error loading faculty data: {e}")

# Helper function to save faculty data
def save_faculty_data():
    try:
        with open(FACULTY_DATA_FILE, "w") as f:
            json.dump(faculty_db, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving faculty data: {e}")

# Helper function to filter faculty based on search criteria
def filter_faculty(faculty_list, query):
    filtered = faculty_list.copy()
    
    # Filter by university
    if query.university:
        filtered = [f for f in filtered if query.university.lower() in f["university_name"].lower()]
    
    # Filter by department
    if query.department:
        filtered = [f for f in filtered if query.department.lower() in f["department_name"].lower()]
    
    # Filter by research areas
    if query.research_areas:
        filtered = [
            f for f in filtered 
            if any(area.lower() in [r.lower() for r in f["research_interests"]] for area in query.research_areas)
        ]
    
    # Filter by keywords (search in name, research interests, and department)
    if query.keywords:
        keywords = query.keywords.lower()
        filtered = [
            f for f in filtered 
            if (keywords in f["name"].lower() or
                keywords in f["department_name"].lower() or
                any(keywords in r.lower() for r in f["research_interests"]))
        ]
    
    return filtered

# Mock matching function (to be replaced with actual matcher in production)
def calculate_compatibility(resume_data, faculty):
    # Simple mock scoring for demonstration
    # For real implementation, use the matcher from resume_matcher/matcher.py
    interests_similarity = 0.0
    
    # Count matching research interests
    resume_interests = [r.lower() for r in resume_data["research_interests"]]
    faculty_interests = [r.lower() for r in faculty["research_interests"]]
    
    matching_interests = sum(1 for r in resume_interests if r in faculty_interests)
    if resume_interests and faculty_interests:
        interests_similarity = matching_interests / max(len(resume_interests), len(faculty_interests))
    
    # Mock education and publication similarity
    education_similarity = 0.5  # Placeholder
    publications_similarity = 0.3  # Placeholder
    
    # Calculate weighted overall score
    overall_score = (interests_similarity * 0.6 + 
                     education_similarity * 0.3 + 
                     publications_similarity * 0.1)
    
    return {
        "faculty_id": faculty["faculty_id"],
        "name": faculty["name"],
        "department": faculty["department_name"],
        "university": faculty["university_name"],
        "interests_similarity": round(interests_similarity, 2),
        "education_similarity": round(education_similarity, 2),
        "publications_similarity": round(publications_similarity, 2),
        "overall_score": round(overall_score, 2)
    }

# Define API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Faculty Matching API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "faculty_count": len(faculty_db)
    }

@app.post("/faculty/search", response_model=List[Faculty])
async def search_faculty(query: SearchQuery = Body(...)):
    """
    Search for faculty members based on criteria.
    """
    filtered = filter_faculty(faculty_db, query)
    return filtered

@app.get("/faculty/{faculty_id}", response_model=Faculty)
async def get_faculty(faculty_id: str):
    """
    Get details for a specific faculty member.
    """
    for faculty in faculty_db:
        if faculty["faculty_id"] == faculty_id:
            return faculty
    raise HTTPException(status_code=404, detail="Faculty not found")

@app.post("/faculty", response_model=Faculty)
async def create_faculty(faculty: Faculty):
    """
    Add a new faculty member to the database.
    """
    faculty_dict = faculty.dict()
    
    # Ensure faculty_id is unique
    if any(f["faculty_id"] == faculty_dict["faculty_id"] for f in faculty_db):
        raise HTTPException(status_code=400, detail="Faculty ID already exists")
    
    faculty_db.append(faculty_dict)
    save_faculty_data()
    
    return faculty_dict

@app.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX).
    """
    # Check file extension
    filename = file.filename
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed")
    
    # Generate unique filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # In real implementation, call resume parser here
    return {
        "filename": unique_filename,
        "file_path": file_path,
        "message": "Resume uploaded successfully. Call /resume/parse with this filename to extract data."
    }

@app.post("/resume/parse", response_model=ResumeData)
async def parse_resume(filename: str = Body(..., embed=True)):
    """
    Parse a previously uploaded resume file.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    # In real implementation, call resume parser from resume_parser module
    # For now, return mock data
    mock_resume_data = {
        "name": "John Doe",
        "research_interests": ["Machine Learning", "Natural Language Processing", "Computer Vision"],
        "education": [
            {
                "degree": "PhD",
                "field": "Computer Science",
                "institution": "Stanford University",
                "year": 2022
            }
        ]
    }
    
    # Save parsed data
    resume_id = os.path.splitext(filename)[0]
    with open(os.path.join(RESUME_DATA_DIR, f"{resume_id}.json"), "w") as f:
        json.dump(mock_resume_data, f, indent=2)
    
    return mock_resume_data

@app.post("/match", response_model=List[MatchResult])
async def match_resume_with_faculty(
    resume_data: ResumeData = Body(...),
    top_k: int = Query(5, ge=1, le=20, description="Number of top matches to return")
):
    """
    Match resume data with faculty profiles and return compatibility scores.
    """
    # Calculate compatibility for all faculty
    matches = []
    for faculty in faculty_db:
        match_result = calculate_compatibility(resume_data.dict(), faculty)
        matches.append(match_result)
    
    # Sort by overall score (descending)
    matches.sort(key=lambda x: x["overall_score"], reverse=True)
    
    # Return top-k matches
    return matches[:top_k]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
