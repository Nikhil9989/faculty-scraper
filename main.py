#!/usr/bin/env python3
"""
Faculty Matcher - Main Control File

This file serves as the main integration point for all components of the
Faculty Matcher system, including:
1. Web scraping of faculty profiles
2. Database operations for storing faculty information
3. Resume parsing functionality
4. Faculty-resume matching algorithm
5. API endpoints for accessing the system

Usage:
    python main.py [command] [options]

Commands:
    scrape          - Run web scraper to collect faculty data
    parse-resume    - Parse a resume and extract relevant information
    match           - Find faculty matches for a parsed resume
    serve           - Start the API server
    setup-db        - Initialize the database

Author: Nikhil
"""

import os
import sys
import json
import logging
import argparse
import psycopg2
import shutil
from datetime import datetime
import uvicorn
import subprocess
import threading
import time
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("faculty_matcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components
# Scraper module
try:
    from scraper import scrape_stanford_cs_faculty, save_to_json
except ImportError:
    logger.error("Failed to import scraper module. Scraping functionality may be limited.")

# Resume parser
try:
    sys.path.append('resume_parser')
    from resume_parser.parser import ResumeParser
except ImportError:
    logger.error("Failed to import resume parser module. Resume parsing functionality may be limited.")

# Resume-faculty matcher
try:
    sys.path.append('resume_matcher')
    from resume_matcher.matcher import ResumeMatcher
except ImportError:
    logger.error("Failed to import resume matcher module. Matching functionality may be limited.")

# Define constants
DATA_DIR = "data"
UPLOAD_DIR = "uploads"
FACULTY_DATA_FILE = os.path.join(DATA_DIR, "faculty_data.json")
RESUME_DATA_DIR = os.path.join(DATA_DIR, "resumes")

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESUME_DATA_DIR, exist_ok=True)

# Database connection parameters
DB_CONFIG = {
    "dbname": "faculty_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Connected to database")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def setup_database():
    """Setup the database with schema from SQL file"""
    try:
        # Create the database if it doesn't exist
        # This requires connecting to the 'postgres' database first
        tmp_config = DB_CONFIG.copy()
        tmp_config["dbname"] = "postgres"
        
        with psycopg2.connect(**tmp_config) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                # Check if database exists
                cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_CONFIG["dbname"],))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
                    logger.info(f"Created database {DB_CONFIG['dbname']}")
        
        # Now connect to the created database and setup schema
        with connect_db() as conn:
            with conn.cursor() as cursor:
                with open("database/schema.sql", "r") as f:
                    sql_script = f.read()
                    cursor.execute(sql_script)
                
                conn.commit()
                logger.info("Database schema setup complete")
        
        return True
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def import_faculty_to_db(faculty_data):
    """
    Import faculty data from the scraped JSON file to the PostgreSQL database
    
    Args:
        faculty_data (list): List of faculty records
    """
    conn = connect_db()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cursor:
                # First, check if Stanford University exists
                cursor.execute("SELECT university_id FROM universities WHERE name = %s", ("Stanford University",))
                result = cursor.fetchone()
                
                if result:
                    university_id = result[0]
                else:
                    # Insert Stanford University
                    cursor.execute(
                        "INSERT INTO universities (name, location, website) VALUES (%s, %s, %s) RETURNING university_id",
                        ("Stanford University", "Stanford, CA", "https://www.stanford.edu")
                    )
                    university_id = cursor.fetchone()[0]
                
                # Check if CS department exists
                cursor.execute(
                    "SELECT department_id FROM departments WHERE university_id = %s AND name = %s",
                    (university_id, "Computer Science")
                )
                result = cursor.fetchone()
                
                if result:
                    department_id = result[0]
                else:
                    # Insert CS department
                    cursor.execute(
                        "INSERT INTO departments (university_id, name, website) VALUES (%s, %s, %s) RETURNING department_id",
                        (university_id, "Computer Science", "https://cs.stanford.edu")
                    )
                    department_id = cursor.fetchone()[0]
                
                # Insert faculty members
                for faculty in faculty_data:
                    name_parts = faculty["name"].split()
                    first_name = name_parts[0]
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""
                    
                    # Check if faculty already exists
                    cursor.execute(
                        "SELECT faculty_id FROM faculty WHERE first_name = %s AND last_name = %s AND department_id = %s",
                        (first_name, last_name, department_id)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        faculty_id = result[0]
                        # Update existing faculty
                        cursor.execute(
                            """
                            UPDATE faculty SET
                                title = %s,
                                email = %s,
                                profile_url = %s,
                                scraped_at = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE faculty_id = %s
                            """,
                            (
                                faculty.get("title", ""),
                                faculty.get("email", ""),
                                faculty.get("profile_url", ""),
                                datetime.now(),
                                faculty_id
                            )
                        )
                    else:
                        # Insert new faculty
                        cursor.execute(
                            """
                            INSERT INTO faculty (
                                department_id,
                                first_name,
                                last_name,
                                title,
                                email,
                                profile_url,
                                scraped_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING faculty_id
                            """,
                            (
                                department_id,
                                first_name,
                                last_name,
                                faculty.get("title", ""),
                                faculty.get("email", ""),
                                faculty.get("profile_url", ""),
                                datetime.now()
                            )
                        )
                        faculty_id = cursor.fetchone()[0]
                    
                    # Insert or update research interests
                    if "research_interests" in faculty and faculty["research_interests"]:
                        # Clear existing interests
                        cursor.execute("DELETE FROM research_interests WHERE faculty_id = %s", (faculty_id,))
                        
                        # Insert new interests
                        for interest in faculty["research_interests"]:
                            cursor.execute(
                                "INSERT INTO research_interests (faculty_id, interest) VALUES (%s, %s)",
                                (faculty_id, interest)
                            )
                    
                    # Insert or update publications
                    if "publications" in faculty and faculty["publications"]:
                        # Clear existing publications
                        cursor.execute("DELETE FROM publications WHERE faculty_id = %s", (faculty_id,))
                        
                        # Insert new publications
                        for pub in faculty["publications"]:
                            # Try to extract year from publication string
                            year = None
                            import re
                            year_match = re.search(r'\b(19|20)\d{2}\b', pub)
                            if year_match:
                                year = int(year_match.group(0))
                            
                            cursor.execute(
                                "INSERT INTO publications (faculty_id, title, year) VALUES (%s, %s, %s)",
                                (faculty_id, pub, year)
                            )
                
                conn.commit()
                logger.info(f"Successfully imported {len(faculty_data)} faculty records to database")
                return True
    except Exception as e:
        logger.error(f"Error importing faculty data to database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def run_scraper():
    """Run the faculty scraper and save results"""
    logger.info("Starting faculty scraper...")
    
    try:
        # Scrape Stanford CS faculty
        faculty_data = scrape_stanford_cs_faculty()
        
        if faculty_data:
            # Save to JSON file
            save_to_json(faculty_data, FACULTY_DATA_FILE)
            
            # Import to database
            import_faculty_to_db(faculty_data)
            
            return True
        else:
            logger.error("No faculty data was collected")
            return False
    except Exception as e:
        logger.error(f"Error in scraper: {e}")
        return False

def parse_resume(pdf_path):
    """
    Parse a resume PDF file and extract relevant information
    
    Args:
        pdf_path (str): Path to the resume PDF file
        
    Returns:
        dict: Parsed resume data
    """
    try:
        logger.info(f"Parsing resume from {pdf_path}")
        
        # Use the ResumeParser class
        parser = ResumeParser(pdf_path)
        parsed_data = parser.parse()
        
        # Save parsed data
        file_name = os.path.basename(pdf_path)
        base_name = os.path.splitext(file_name)[0]
        output_file = os.path.join(RESUME_DATA_DIR, f"{base_name}.json")
        
        with open(output_file, "w") as f:
            json.dump(parsed_data, f, indent=2)
        
        logger.info(f"Resume parsed successfully. Data saved to {output_file}")
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return None

def get_faculty_from_db():
    """
    Retrieve faculty data from the database
    
    Returns:
        list: List of faculty records
    """
    conn = connect_db()
    if not conn:
        return []
    
    try:
        with conn:
            with conn.cursor() as cursor:
                # Query to join faculty with universities, departments, research interests, and publications
                query = """
                SELECT 
                    f.faculty_id,
                    f.first_name,
                    f.last_name,
                    f.title,
                    f.email,
                    f.profile_url,
                    d.name as department_name,
                    u.name as university_name,
                    array_agg(DISTINCT ri.interest) as research_interests,
                    array_agg(DISTINCT p.title) as publications
                FROM 
                    faculty f
                    JOIN departments d ON f.department_id = d.department_id
                    JOIN universities u ON d.university_id = u.university_id
                    LEFT JOIN research_interests ri ON f.faculty_id = ri.faculty_id
                    LEFT JOIN publications p ON f.faculty_id = p.faculty_id
                GROUP BY
                    f.faculty_id, f.first_name, f.last_name, f.title, f.email, f.profile_url,
                    d.name, u.name
                """
                cursor.execute(query)
                
                # Fetch results
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
                faculty_list = []
                for row in results:
                    faculty_dict = {
                        "faculty_id": row[0],
                        "name": f"{row[1]} {row[2]}".strip(),
                        "title": row[3],
                        "email": row[4],
                        "profile_url": row[5],
                        "department_name": row[6],
                        "university_name": row[7],
                        "research_interests": [ri for ri in row[8] if ri],  # Filter out None values
                        "publications": [p for p in row[9] if p]  # Filter out None values
                    }
                    faculty_list.append(faculty_dict)
                
                logger.info(f"Retrieved {len(faculty_list)} faculty records from database")
                return faculty_list
    except Exception as e:
        logger.error(f"Error retrieving faculty data from database: {e}")
        return []
    finally:
        if conn:
            conn.close()

def match_resume_with_faculty(resume_data, use_transformer=False):
    """
    Match a parsed resume with faculty profiles
    
    Args:
        resume_data (dict): Parsed resume data
        use_transformer (bool): Whether to use transformer models for better matching
        
    Returns:
        list: Ranked faculty matches with similarity scores
    """
    try:
        logger.info("Starting faculty matching process")
        
        # Get faculty data
        faculty_profiles = get_faculty_from_db()
        
        if not faculty_profiles:
            # Try loading from JSON if database retrieval failed
            if os.path.exists(FACULTY_DATA_FILE):
                with open(FACULTY_DATA_FILE, "r") as f:
                    faculty_profiles = json.load(f)
            
            if not faculty_profiles:
                logger.error("No faculty data available for matching")
                return []
        
        # Create matcher instance
        matcher = ResumeMatcher(use_transformer=use_transformer, use_spacy=True)
        
        # Perform matching
        matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)
        
        logger.info(f"Found {len(matches)} faculty matches")
        return matches
    except Exception as e:
        logger.error(f"Error matching resume with faculty: {e}")
        return []

def start_api_server():
    """Start the FastAPI server for the faculty API"""
    logger.info("Starting Faculty Matcher API server...")
    
    # Change to the API directory
    api_dir = os.path.join(os.getcwd(), "faculty_api")
    
    if os.path.exists(api_dir):
        # Run the API server
        try:
            # Use uvicorn to run the API
            uvicorn.run("faculty_api.main:app", host="0.0.0.0", port=8000, reload=True)
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            return False
    else:
        logger.error(f"API directory not found: {api_dir}")
        return False

def start_resume_parser_server():
    """Start the Flask server for the resume parser API"""
    logger.info("Starting Resume Parser API server...")
    
    # Change to the resume parser directory
    parser_dir = os.path.join(os.getcwd(), "resume_parser")
    
    if os.path.exists(parser_dir):
        # Run the parser server
        try:
            # Import and run the Flask app
            sys.path.append(parser_dir)
            from resume_parser.app import app
            app.run(host="0.0.0.0", port=5000)
        except Exception as e:
            logger.error(f"Error starting resume parser server: {e}")
            return False
    else:
        logger.error(f"Resume parser directory not found: {parser_dir}")
        return False

def start_all_services():
    """Start all services in separate threads"""
    logger.info("Starting all services...")
    
    # Start the API server in a separate thread
    api_thread = threading.Thread(target=start_api_server)
    api_thread.daemon = True
    api_thread.start()
    
    # Start the resume parser server in a separate thread
    parser_thread = threading.Thread(target=start_resume_parser_server)
    parser_thread.daemon = True
    parser_thread.start()
    
    logger.info("All services started. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping services...")
        sys.exit(0)

def main():
    """Main entry point for the application"""
    # Define command line arguments
    parser = argparse.ArgumentParser(description="Faculty Matcher System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scraper command
    scraper_parser = subparsers.add_parser("scrape", help="Run web scraper to collect faculty data")
    
    # Parse resume command
    resume_parser = subparsers.add_parser("parse-resume", help="Parse a resume PDF file")
    resume_parser.add_argument("pdf_path", help="Path to the resume PDF file")
    
    # Match command
    match_parser = subparsers.add_parser("match", help="Match a resume with faculty profiles")
    match_parser.add_argument("resume_json", help="Path to the parsed resume JSON file")
    match_parser.add_argument("--use-transformer", action="store_true", help="Use transformer models for better matching")
    
    # API server command
    api_parser = subparsers.add_parser("serve", help="Start the API server")
    
    # Database setup command
    db_parser = subparsers.add_parser("setup-db", help="Initialize the database")
    
    # All services command
    all_parser = subparsers.add_parser("start-all", help="Start all services")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "scrape":
        run_scraper()
    elif args.command == "parse-resume":
        parse_resume(args.pdf_path)
    elif args.command == "match":
        # Load resume data from JSON
        try:
            with open(args.resume_json, "r") as f:
                resume_data = json.load(f)
            
            matches = match_resume_with_faculty(resume_data, args.use_transformer)
            
            # Print matches
            print(f"\nFound {len(matches)} faculty matches:")
            for i, match in enumerate(matches, 1):
                print(f"\nMatch #{i}: {match['name']} ({match['university']})")
                print(f"Overall Score: {match['overall_score']}")
                print(f"Research Interests Similarity: {match['interests_similarity']}")
                print(f"Education Similarity: {match['education_similarity']}")
                print(f"Publications Similarity: {match['publications_similarity']}")
        except Exception as e:
            logger.error(f"Error processing match command: {e}")
    elif args.command == "serve":
        start_api_server()
    elif args.command == "setup-db":
        setup_database()
    elif args.command == "start-all":
        start_all_services()
    else:
        # No command provided, print help
        parser.print_help()

if __name__ == "__main__":
    main()
