"""
Resume-Faculty Matching Algorithm

This module provides algorithms to match student resumes with faculty profiles
based on research interests and other relevant information.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResumeMatcher:
    """
    A class to match resumes with faculty profiles using text similarity metrics.
    """
    
    def __init__(self):
        """Initialize the ResumeMatcher with a TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=5000,
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
    
    def preprocess_text(self, text_list):
        """
        Preprocess a list of text items by joining them and normalizing.
        
        Args:
            text_list (list): List of text strings
            
        Returns:
            str: Joined and normalized text
        """
        if not text_list:
            return ""
        
        # Handle both string lists and string inputs
        if isinstance(text_list, str):
            return text_list.lower().strip()
        
        # Join all items with space and convert to lowercase
        return " ".join(str(item) for item in text_list).lower().strip()
    
    def calculate_similarity(self, text1, text2):
        """
        Calculate cosine similarity between two texts using TF-IDF.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Cosine similarity score between 0 and 1
        """
        # Handle empty inputs
        if not text1 or not text2:
            return 0.0
        
        # Preprocess texts
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)
        
        # If either text is empty after preprocessing, return 0
        if not processed_text1 or not processed_text2:
            return 0.0
        
        try:
            # Combine texts for vectorization
            texts = [processed_text1, processed_text2]
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def match_resume_with_faculty(self, resume_data, faculty_profiles):
        """
        Match a resume with multiple faculty profiles and return ranked matches.
        
        Args:
            resume_data (dict): Parsed resume data with research interests
            faculty_profiles (list): List of faculty profile dictionaries
            
        Returns:
            list: Ranked list of faculty matches with similarity scores
        """
        matches = []
        
        # Extract resume research interests
        resume_interests = resume_data.get('research_interests', [])
        resume_interests_text = self.preprocess_text(resume_interests)
        
        # Calculate similarity with each faculty profile
        for faculty in faculty_profiles:
            # Extract faculty research interests
            faculty_interests = faculty.get('research_interests', [])
            faculty_interests_text = self.preprocess_text(faculty_interests)
            
            # Calculate similarity score for research interests
            interests_similarity = self.calculate_similarity(
                resume_interests_text, faculty_interests_text
            )
            
            # Calculate additional similarity metrics (if available)
            education_similarity = 0.0
            publications_similarity = 0.0
            
            # Compare education if available
            if 'education' in resume_data and 'education' in faculty:
                # Extract education details
                resume_education = [
                    f"{edu.get('degree', '')} {edu.get('field', '')}" 
                    for edu in resume_data.get('education', [])
                ]
                faculty_education = [
                    f"{edu.get('degree', '')} {edu.get('field', '')}" 
                    for edu in faculty.get('education', [])
                ]
                
                education_similarity = self.calculate_similarity(
                    self.preprocess_text(resume_education),
                    self.preprocess_text(faculty_education)
                )
            
            # Compare publications if available
            if 'publications' in resume_data and 'publications' in faculty:
                resume_publications = resume_data.get('publications', [])
                faculty_publications = faculty.get('publications', [])
                
                publications_similarity = self.calculate_similarity(
                    self.preprocess_text(resume_publications),
                    self.preprocess_text(faculty_publications)
                )
            
            # Calculate weighted overall score
            # Research interests are given the highest weight
            overall_score = (
                interests_similarity * 0.7 +  # 70% weight to research interests
                education_similarity * 0.2 +  # 20% weight to education
                publications_similarity * 0.1  # 10% weight to publications
            )
            
            # Add to matches
            matches.append({
                'faculty_id': faculty.get('faculty_id', ''),
                'name': faculty.get('name', ''),
                'department': faculty.get('department_name', ''),
                'university': faculty.get('university_name', ''),
                'interests_similarity': round(interests_similarity, 2),
                'education_similarity': round(education_similarity, 2),
                'publications_similarity': round(publications_similarity, 2),
                'overall_score': round(overall_score, 2)
            })
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matches

def main():
    """
    Example usage of the ResumeMatcher class.
    """
    # Create test data
    resume_data = {
        'name': 'John Doe',
        'research_interests': [
            'Machine Learning',
            'Natural Language Processing',
            'Computer Vision'
        ],
        'education': [
            {
                'degree': 'PhD',
                'field': 'Computer Science',
                'institution': 'Stanford University',
                'year': 2022
            }
        ]
    }
    
    faculty_profiles = [
        {
            'faculty_id': 1,
            'name': 'Dr. Alice Smith',
            'department_name': 'Computer Science',
            'university_name': 'Stanford University',
            'research_interests': [
                'Machine Learning',
                'Artificial Intelligence',
                'Deep Learning'
            ]
        },
        {
            'faculty_id': 2,
            'name': 'Dr. Bob Johnson',
            'department_name': 'Electrical Engineering',
            'university_name': 'MIT',
            'research_interests': [
                'Robotics',
                'Computer Vision',
                'Sensor Networks'
            ]
        }
    ]
    
    # Create matcher and find matches
    matcher = ResumeMatcher()
    matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)
    
    # Print results
    for i, match in enumerate(matches, 1):
        print(f"\nMatch #{i}: {match['name']} ({match['university']})")
        print(f"Overall Score: {match['overall_score']}")
        print(f"Research Interests Similarity: {match['interests_similarity']}")

if __name__ == "__main__":
    main()
