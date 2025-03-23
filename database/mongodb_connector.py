"""
MongoDB connector for faculty database.

This module provides functions for connecting to MongoDB and interacting with the faculty data.
"""

import datetime
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoDBConnector:
    """
    A class to handle MongoDB connections and operations for faculty data.
    """
    
    def __init__(self, db_name='faculty_db', host='localhost', port=27017):
        """
        Initialize the MongoDB connector.
        
        Args:
            db_name (str): Database name
            host (str): MongoDB host address
            port (int): MongoDB port
        """
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        
    def close(self):
        """Close the MongoDB connection"""
        self.client.close()
        
    def insert_university(self, university_data):
        """
        Insert a new university into the database.
        
        Args:
            university_data (dict): University information
            
        Returns:
            str: ID of the inserted university
        """
        # Add timestamps
        university_data['created_at'] = datetime.datetime.now()
        university_data['updated_at'] = datetime.datetime.now()
        
        result = self.db.universities.insert_one(university_data)
        return str(result.inserted_id)
    
    def insert_faculty(self, faculty_data):
        """
        Insert a new faculty member into the database.
        
        Args:
            faculty_data (dict): Faculty information
            
        Returns:
            str: ID of the inserted faculty
        """
        # Add timestamps
        faculty_data['created_at'] = datetime.datetime.now()
        faculty_data['updated_at'] = datetime.datetime.now()
        
        # Convert scraped_at to datetime if it's a string
        if 'scraped_at' in faculty_data and isinstance(faculty_data['scraped_at'], str):
            faculty_data['scraped_at'] = datetime.datetime.fromisoformat(faculty_data['scraped_at'])
        
        result = self.db.faculty.insert_one(faculty_data)
        return str(result.inserted_id)
    
    def bulk_insert_faculty(self, faculty_data_list):
        """
        Insert multiple faculty members into the database.
        
        Args:
            faculty_data_list (list): List of faculty information dictionaries
            
        Returns:
            list: IDs of the inserted faculty members
        """
        # Add timestamps to all records
        now = datetime.datetime.now()
        for faculty in faculty_data_list:
            faculty['created_at'] = now
            faculty['updated_at'] = now
            
            # Convert scraped_at to datetime if it's a string
            if 'scraped_at' in faculty and isinstance(faculty['scraped_at'], str):
                faculty['scraped_at'] = datetime.datetime.fromisoformat(faculty['scraped_at'])
        
        result = self.db.faculty.insert_many(faculty_data_list)
        return [str(id) for id in result.inserted_ids]
    
    def get_faculty_by_university(self, university_name):
        """
        Get all faculty members from a specific university.
        
        Args:
            university_name (str): Name of the university
            
        Returns:
            list: List of faculty members (as dictionaries)
        """
        cursor = self.db.faculty.find({'university_name': university_name})
        
        # Convert ObjectId to string for JSON serialization
        faculty_list = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            faculty_list.append(doc)
            
        return faculty_list
    
    def get_faculty_by_research_interest(self, interest_keyword):
        """
        Get faculty members with a specific research interest.
        
        Args:
            interest_keyword (str): Keyword to search in research interests
            
        Returns:
            list: List of faculty members (as dictionaries)
        """
        cursor = self.db.faculty.find(
            {'$text': {'$search': interest_keyword}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})])
        
        # Convert ObjectId to string for JSON serialization
        faculty_list = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            faculty_list.append(doc)
            
        return faculty_list
    
    def import_from_json(self, json_file_path):
        """
        Import faculty data from a JSON file.
        
        Args:
            json_file_path (str): Path to the JSON file
            
        Returns:
            int: Number of faculty records imported
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract unique universities
        universities = {}
        for faculty in data:
            if 'university' in faculty and faculty['university'] not in universities:
                universities[faculty['university']] = {
                    'name': faculty['university'],
                    'departments': []
                }
                
            # Add department if not already added
            if 'department' in faculty:
                dept_exists = False
                for dept in universities[faculty['university']]['departments']:
                    if dept['name'] == faculty['department']:
                        dept_exists = True
                        break
                
                if not dept_exists:
                    universities[faculty['university']]['departments'].append({
                        'name': faculty['department']
                    })
        
        # Insert universities
        for university_name, university_data in universities.items():
            self.insert_university(university_data)
        
        # Format faculty data for MongoDB
        faculty_data_list = []
        for faculty in data:
            # Standardize field names for MongoDB schema
            formatted_faculty = {
                'first_name': faculty.get('name', '').split()[0] if faculty.get('name') else '',
                'last_name': ' '.join(faculty.get('name', '').split()[1:]) if faculty.get('name') else '',
                'title': faculty.get('title', ''),
                'university_name': faculty.get('university', ''),
                'department_name': faculty.get('department', ''),
                'email': faculty.get('email', ''),
                'profile_url': faculty.get('profile_url', ''),
                'research_interests': faculty.get('research_interests', []),
                'publications': faculty.get('publications', []),
                'scraped_at': faculty.get('scraped_at', datetime.datetime.now())
            }
            
            faculty_data_list.append(formatted_faculty)
        
        # Insert faculty members
        if faculty_data_list:
            self.bulk_insert_faculty(faculty_data_list)
        
        return len(faculty_data_list)


def main():
    """Example usage of the MongoDB connector"""
    # Example code to demonstrate usage
    connector = MongoDBConnector()
    
    # Example: Import data from a JSON file
    print("To import data from a JSON file:")
    print("connector.import_from_json('faculty_data.json')")
    
    # Example: Query faculty by university
    print("\nTo query faculty by university:")
    print("faculty = connector.get_faculty_by_university('Stanford University')")
    
    # Example: Query faculty by research interest
    print("\nTo query faculty by research interest:")
    print("faculty = connector.get_faculty_by_research_interest('machine learning')")
    
    connector.close()

if __name__ == "__main__":
    main()
