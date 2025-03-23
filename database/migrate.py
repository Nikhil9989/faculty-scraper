#!/usr/bin/env python3
"""
Migration tool for faculty data between PostgreSQL and MongoDB.

This script provides functions to migrate data from PostgreSQL to MongoDB and vice versa.
"""

import argparse
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
from mongodb_connector import MongoDBConnector

def pg_to_mongo(pg_conn_string, mongo_db_name='faculty_db', mongo_host='localhost', mongo_port=27017):
    """
    Migrate data from PostgreSQL to MongoDB.
    
    Args:
        pg_conn_string (str): PostgreSQL connection string
        mongo_db_name (str): MongoDB database name
        mongo_host (str): MongoDB host
        mongo_port (int): MongoDB port
    
    Returns:
        int: Number of faculty records migrated
    """
    print("Migrating data from PostgreSQL to MongoDB...")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(pg_conn_string)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Initialize MongoDB connector
    mongo = MongoDBConnector(db_name=mongo_db_name, host=mongo_host, port=mongo_port)
    
    # Step 1: Extract universities and departments
    print("Extracting universities and departments...")
    cur.execute("""
        SELECT u.university_id, u.name, u.location, u.website, 
               d.department_id, d.name as dept_name, d.website as dept_website
        FROM universities u
        LEFT JOIN departments d ON u.university_id = d.university_id
    """)
    
    rows = cur.fetchall()
    
    # Group departments by university
    universities = {}
    for row in rows:
        if row['university_id'] not in universities:
            universities[row['university_id']] = {
                'name': row['name'],
                'location': row['location'],
                'website': row['website'],
                'departments': []
            }
        
        if row['department_id'] is not None:
            universities[row['university_id']]['departments'].append({
                'name': row['dept_name'],
                'website': row['dept_website']
            })
    
    # Insert universities into MongoDB
    for university_data in universities.values():
        mongo.insert_university(university_data)
    
    # Step 2: Extract faculty data
    print("Extracting faculty data...")
    cur.execute("""
        SELECT f.faculty_id, f.first_name, f.last_name, f.title, f.email, f.profile_url, 
               f.scraped_at, d.name as department_name, u.name as university_name
        FROM faculty f
        JOIN departments d ON f.department_id = d.department_id
        JOIN universities u ON d.university_id = u.university_id
    """)
    
    faculty_rows = cur.fetchall()
    faculty_data = []
    
    for faculty in faculty_rows:
        # Get research interests for this faculty
        cur.execute("""
            SELECT interest FROM research_interests WHERE faculty_id = %s
        """, (faculty['faculty_id'],))
        
        interests = [row['interest'] for row in cur.fetchall()]
        
        # Get publications for this faculty
        cur.execute("""
            SELECT title, authors, year, venue, url FROM publications WHERE faculty_id = %s
        """, (faculty['faculty_id'],))
        
        publications = cur.fetchall()
        
        # Format faculty data for MongoDB
        faculty_doc = {
            'first_name': faculty['first_name'],
            'last_name': faculty['last_name'],
            'title': faculty['title'],
            'email': faculty['email'],
            'profile_url': faculty['profile_url'],
            'university_name': faculty['university_name'],
            'department_name': faculty['department_name'],
            'research_interests': interests,
            'publications': publications,
            'scraped_at': faculty['scraped_at'] if faculty['scraped_at'] else datetime.datetime.now()
        }
        
        faculty_data.append(faculty_doc)
    
    # Insert faculty data into MongoDB
    if faculty_data:
        mongo.bulk_insert_faculty(faculty_data)
    
    # Close connections
    cur.close()
    conn.close()
    mongo.close()
    
    print(f"Migration complete. {len(faculty_data)} faculty records migrated to MongoDB.")
    return len(faculty_data)

def mongo_to_pg(pg_conn_string, mongo_db_name='faculty_db', mongo_host='localhost', mongo_port=27017):
    """
    Migrate data from MongoDB to PostgreSQL.
    
    Args:
        pg_conn_string (str): PostgreSQL connection string
        mongo_db_name (str): MongoDB database name
        mongo_host (str): MongoDB host
        mongo_port (int): MongoDB port
    
    Returns:
        int: Number of faculty records migrated
    """
    print("Migrating data from MongoDB to PostgreSQL...")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(pg_conn_string)
    cur = conn.cursor()
    
    # Initialize MongoDB connector
    mongo = MongoDBConnector(db_name=mongo_db_name, host=mongo_host, port=mongo_port)
    
    # Step 1: Get all universities from MongoDB
    client = mongo.client
    db = client[mongo_db_name]
    mongo_universities = list(db.universities.find())
    
    # Create dictionary to store id mappings (MongoDB _id -> PostgreSQL id)
    university_id_map = {}
    department_id_map = {}
    
    # Step 2: Insert universities into PostgreSQL
    for mongo_university in mongo_universities:
        # Check if university already exists
        cur.execute("SELECT university_id FROM universities WHERE name = %s", (mongo_university['name'],))
        result = cur.fetchone()
        
        if result:
            # University exists, use existing ID
            university_id = result[0]
        else:
            # Insert new university
            cur.execute("""
                INSERT INTO universities (name, location, website, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s) RETURNING university_id
            """, (
                mongo_university['name'],
                mongo_university.get('location', ''),
                mongo_university.get('website', ''),
                datetime.datetime.now(),
                datetime.datetime.now()
            ))
            university_id = cur.fetchone()[0]
        
        # Store mapping
        university_id_map[str(mongo_university['_id'])] = university_id
        
        # Step 3: Insert departments
        if 'departments' in mongo_university:
            for dept in mongo_university['departments']:
                # Check if department already exists
                cur.execute("SELECT department_id FROM departments WHERE name = %s AND university_id = %s", 
                          (dept['name'], university_id))
                result = cur.fetchone()
                
                if result:
                    # Department exists, use existing ID
                    department_id = result[0]
                else:
                    # Insert new department
                    cur.execute("""
                        INSERT INTO departments (university_id, name, website, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s) RETURNING department_id
                    """, (
                        university_id,
                        dept['name'],
                        dept.get('website', ''),
                        datetime.datetime.now(),
                        datetime.datetime.now()
                    ))
                    department_id = cur.fetchone()[0]
                
                # Store mapping (using university-department combination as key)
                dept_key = f"{mongo_university['name']}-{dept['name']}"
                department_id_map[dept_key] = department_id
    
    # Step 4: Get all faculty from MongoDB
    mongo_faculty = list(db.faculty.find())
    
    # Step 5: Insert faculty into PostgreSQL
    faculty_count = 0
    for faculty in mongo_faculty:
        try:
            # Get department ID
            dept_key = f"{faculty['university_name']}-{faculty['department_name']}"
            if dept_key not in department_id_map:
                print(f"Warning: Department {dept_key} not found in mapping. Creating it.")
                
                # Look up university ID
                cur.execute("SELECT university_id FROM universities WHERE name = %s", (faculty['university_name'],))
                result = cur.fetchone()
                
                if not result:
                    # Need to create university first
                    cur.execute("""
                        INSERT INTO universities (name, created_at, updated_at)
                        VALUES (%s, %s, %s) RETURNING university_id
                    """, (
                        faculty['university_name'],
                        datetime.datetime.now(),
                        datetime.datetime.now()
                    ))
                    university_id = cur.fetchone()[0]
                else:
                    university_id = result[0]
                
                # Create department
                cur.execute("""
                    INSERT INTO departments (university_id, name, created_at, updated_at)
                    VALUES (%s, %s, %s, %s) RETURNING department_id
                """, (
                    university_id,
                    faculty['department_name'],
                    datetime.datetime.now(),
                    datetime.datetime.now()
                ))
                department_id = cur.fetchone()[0]
                department_id_map[dept_key] = department_id
            
            # Get department ID from mapping
            department_id = department_id_map[dept_key]
            
            # Check if faculty already exists
            cur.execute("""
                SELECT faculty_id FROM faculty 
                WHERE first_name = %s AND last_name = %s AND department_id = %s
            """, (faculty['first_name'], faculty['last_name'], department_id))
            
            result = cur.fetchone()
            
            if result:
                # Faculty exists, use existing ID
                faculty_id = result[0]
                
                # Update faculty information
                cur.execute("""
                    UPDATE faculty SET 
                    title = %s, email = %s, profile_url = %s, updated_at = %s
                    WHERE faculty_id = %s
                """, (
                    faculty.get('title', ''),
                    faculty.get('email', ''),
                    faculty.get('profile_url', ''),
                    datetime.datetime.now(),
                    faculty_id
                ))
            else:
                # Insert new faculty
                scraped_at = faculty.get('scraped_at')
                if isinstance(scraped_at, str):
                    scraped_at = datetime.datetime.fromisoformat(scraped_at)
                
                cur.execute("""
                    INSERT INTO faculty (
                        department_id, first_name, last_name, title, email, 
                        profile_url, scraped_at, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING faculty_id
                """, (
                    department_id,
                    faculty['first_name'],
                    faculty['last_name'],
                    faculty.get('title', ''),
                    faculty.get('email', ''),
                    faculty.get('profile_url', ''),
                    scraped_at if scraped_at else datetime.datetime.now(),
                    datetime.datetime.now(),
                    datetime.datetime.now()
                ))
                faculty_id = cur.fetchone()[0]
            
            # Insert research interests
            if 'research_interests' in faculty:
                # First delete existing interests
                cur.execute("DELETE FROM research_interests WHERE faculty_id = %s", (faculty_id,))
                
                # Then insert new ones
                for interest in faculty['research_interests']:
                    cur.execute("""
                        INSERT INTO research_interests (faculty_id, interest, created_at)
                        VALUES (%s, %s, %s)
                    """, (
                        faculty_id,
                        interest,
                        datetime.datetime.now()
                    ))
            
            # Insert publications
            if 'publications' in faculty:
                # First delete existing publications
                cur.execute("DELETE FROM publications WHERE faculty_id = %s", (faculty_id,))
                
                # Then insert new ones
                for pub in faculty['publications']:
                    # Handle different publication formats (could be a dict or string)
                    if isinstance(pub, dict):
                        cur.execute("""
                            INSERT INTO publications (
                                faculty_id, title, authors, year, venue, url, created_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            faculty_id,
                            pub.get('title', ''),
                            pub.get('authors', ''),
                            pub.get('year'),
                            pub.get('venue', ''),
                            pub.get('url', ''),
                            datetime.datetime.now()
                        ))
                    else:
                        # Simple string publication
                        cur.execute("""
                            INSERT INTO publications (faculty_id, title, created_at)
                            VALUES (%s, %s, %s)
                        """, (
                            faculty_id,
                            pub,
                            datetime.datetime.now()
                        ))
            
            faculty_count += 1
            
        except Exception as e:
            print(f"Error migrating faculty {faculty.get('first_name', '')} {faculty.get('last_name', '')}: {e}")
            continue
    
    # Commit the transaction
    conn.commit()
    
    # Close connections
    cur.close()
    conn.close()
    mongo.close()
    
    print(f"Migration complete. {faculty_count} faculty records migrated to PostgreSQL.")
    return faculty_count

def main():
    """Main function to handle command-line arguments and run the migration."""
    parser = argparse.ArgumentParser(description="Migrate faculty data between PostgreSQL and MongoDB.")
    parser.add_argument('--direction', choices=['pg_to_mongo', 'mongo_to_pg'], required=True,
                       help="Direction of migration: pg_to_mongo or mongo_to_pg")
    parser.add_argument('--pg-conn', required=True,
                       help="PostgreSQL connection string, e.g., 'dbname=faculty_db user=postgres password=postgres'")
    parser.add_argument('--mongo-db', default='faculty_db',
                       help="MongoDB database name (default: faculty_db)")
    parser.add_argument('--mongo-host', default='localhost',
                       help="MongoDB host (default: localhost)")
    parser.add_argument('--mongo-port', type=int, default=27017,
                       help="MongoDB port (default: 27017)")
    
    args = parser.parse_args()
    
    if args.direction == 'pg_to_mongo':
        pg_to_mongo(args.pg_conn, args.mongo_db, args.mongo_host, args.mongo_port)
    else:
        mongo_to_pg(args.pg_conn, args.mongo_db, args.mongo_host, args.mongo_port)

if __name__ == "__main__":
    main()
