"""
Resume-Faculty Matching Algorithm

This module provides algorithms to match student resumes with faculty profiles
based on research interests and other relevant information, using advanced NLP techniques.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import logging
import re
from sentence_transformers import SentenceTransformer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Make sure NLTK resources are available
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Could not download NLTK resources: {e}")

class ResumeMatcher:
    """
    A class to match resumes with faculty profiles using advanced NLP techniques.
    """
    
    def __init__(self, use_transformer=True, use_spacy=True):
        """
        Initialize the ResumeMatcher with NLP models.
        
        Args:
            use_transformer (bool): Whether to use BERT transformer models
            use_spacy (bool): Whether to use spaCy for entity extraction
        """
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=5000,
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        
        self.use_transformer = use_transformer
        self.use_spacy = use_spacy
        
        # Initialize models if requested
        if self.use_transformer:
            try:
                self.transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.warning(f"Could not load transformer model: {e}")
                logger.warning("Falling back to TF-IDF only")
                self.use_transformer = False
        
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_md")  # Medium-sized model with word vectors
                logger.info("Loaded spaCy model")
            except Exception as e:
                logger.warning(f"Could not load spaCy model: {e}")
                logger.warning("Falling back to simpler NLP processing")
                self.use_spacy = False
    
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
            text = text_list
        else:
            # Join all items with space
            text = " ".join(str(item) for item in text_list)
        
        # Convert to lowercase
        text = text.lower()
        
        # Apply more advanced preprocessing if spaCy is available
        if self.use_spacy:
            # Process with spaCy to lemmatize and remove stopwords
            doc = self.nlp(text)
            # Keep only meaningful tokens (non-stopwords, non-punctuation)
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            text = " ".join(tokens)
        else:
            # Fallback to basic NLTK preprocessing
            try:
                # Tokenize and remove stopwords
                stop_words = set(stopwords.words('english'))
                word_tokens = word_tokenize(text)
                filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
                text = " ".join(filtered_text)
            except Exception as e:
                logger.warning(f"Basic preprocessing failed, using raw text: {e}")
        
        return text.strip()
    
    def calculate_tfidf_similarity(self, text1, text2):
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
            logger.error(f"Error calculating TF-IDF similarity: {str(e)}")
            return 0.0
    
    def calculate_transformer_similarity(self, text1, text2):
        """
        Calculate semantic similarity using BERT embeddings.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Cosine similarity score between 0 and 1
        """
        if not self.use_transformer:
            return 0.0
            
        # Handle empty inputs
        if not text1 or not text2:
            return 0.0
        
        try:
            # Create embeddings
            embedding1 = self.transformer_model.encode([text1])[0]
            embedding2 = self.transformer_model.encode([text2])[0]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                embedding1.reshape(1, -1), 
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating transformer similarity: {str(e)}")
            return 0.0
    
    def calculate_spacy_similarity(self, text1, text2):
        """
        Calculate semantic similarity using spaCy word vectors.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not self.use_spacy:
            return 0.0
            
        # Handle empty inputs
        if not text1 or not text2:
            return 0.0
        
        try:
            # Process texts with spaCy
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            
            # Calculate similarity
            similarity = doc1.similarity(doc2)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating spaCy similarity: {str(e)}")
            return 0.0
    
    def calculate_combined_similarity(self, text1, text2):
        """
        Calculate similarity using a combination of methods.
        
        Args:
            text1 (str or list): First text or list of texts
            text2 (str or list): Second text or list of texts
            
        Returns:
            float: Combined similarity score between 0 and 1
        """
        # Preprocess and join lists if needed
        if isinstance(text1, list):
            text1 = " ".join(str(item) for item in text1)
        if isinstance(text2, list):
            text2 = " ".join(str(item) for item in text2)
        
        # Calculate similarities using different methods
        tfidf_sim = self.calculate_tfidf_similarity(text1, text2)
        
        # Default weights
        tfidf_weight = 0.4
        transformer_weight = 0.4
        spacy_weight = 0.2
        total_weight = tfidf_weight
        
        # Start with TF-IDF similarity
        combined_sim = tfidf_sim * tfidf_weight
        
        # Add transformer similarity if available
        if self.use_transformer:
            transformer_sim = self.calculate_transformer_similarity(text1, text2)
            combined_sim += transformer_sim * transformer_weight
            total_weight += transformer_weight
        
        # Add spaCy similarity if available
        if self.use_spacy:
            spacy_sim = self.calculate_spacy_similarity(text1, text2)
            combined_sim += spacy_sim * spacy_weight
            total_weight += spacy_weight
        
        # Normalize by total weight
        if total_weight > 0:
            combined_sim /= total_weight
        
        return combined_sim
    
    def extract_keywords(self, text):
        """
        Extract important keywords from text.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of extracted keywords
        """
        if not text:
            return []
        
        if self.use_spacy:
            # Extract keywords using spaCy
            doc = self.nlp(text)
            
            # Get nouns and proper nouns as keywords
            keywords = [token.text for token in doc if token.pos_ in ('NOUN', 'PROPN')]
            
            # Get named entities
            entities = [ent.text for ent in doc.ents if ent.label_ in ('ORG', 'PRODUCT', 'GPE', 'WORK_OF_ART')]
            
            # Combine and deduplicate
            keywords = list(set(keywords + entities))
            
            return keywords
        else:
            # Fallback to basic keyword extraction
            # Remove stopwords and keep words with capital letters or > 3 chars
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
            try:
                stop_words = set(stopwords.words('english'))
                words = [word for word in words if word.lower() not in stop_words]
            except:
                pass
            
            return words
    
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
        resume_interests_text = " ".join(str(interest) for interest in resume_interests)
        
        # Extract resume education info
        resume_education = []
        for edu in resume_data.get('education', []):
            edu_text = f"{edu.get('degree', '')} {edu.get('field', '')} {edu.get('institution', '')}"
            resume_education.append(edu_text)
        resume_education_text = " ".join(resume_education)
        
        # Calculate similarity with each faculty profile
        for faculty in faculty_profiles:
            # Extract faculty research interests
            faculty_interests = faculty.get('research_interests', [])
            faculty_interests_text = " ".join(str(interest) for interest in faculty_interests)
            
            # Calculate similarity score for research interests using advanced methods
            interests_similarity = self.calculate_combined_similarity(
                resume_interests_text, faculty_interests_text
            )
            
            # Extract faculty education if available
            faculty_education = []
            for edu in faculty.get('education', []):
                edu_text = f"{edu.get('degree', '')} {edu.get('field', '')} {edu.get('institution', '')}"
                faculty_education.append(edu_text)
            faculty_education_text = " ".join(faculty_education)
            
            # Calculate education similarity
            education_similarity = self.calculate_combined_similarity(
                resume_education_text, faculty_education_text
            ) if faculty_education else 0.0
            
            # Calculate publication similarity if available
            publications_similarity = 0.0
            if 'publications' in resume_data and 'publications' in faculty:
                resume_pubs = resume_data.get('publications', [])
                faculty_pubs = faculty.get('publications', [])
                
                # Convert to text
                resume_pubs_text = " ".join(str(pub) for pub in resume_pubs)
                faculty_pubs_text = " ".join(str(pub) for pub in faculty_pubs)
                
                # Calculate similarity
                publications_similarity = self.calculate_combined_similarity(
                    resume_pubs_text, faculty_pubs_text
                )
            
            # Extract and compare keywords for additional matching
            if resume_interests_text and faculty_interests_text:
                resume_keywords = self.extract_keywords(resume_interests_text)
                faculty_keywords = self.extract_keywords(faculty_interests_text)
                
                # Calculate keyword overlap
                if resume_keywords and faculty_keywords:
                    common_keywords = set(k.lower() for k in resume_keywords) & set(k.lower() for k in faculty_keywords)
                    keyword_match = len(common_keywords) / max(len(resume_keywords), 1)
                else:
                    keyword_match = 0.0
            else:
                keyword_match = 0.0
            
            # Calculate weighted overall score with the new components
            overall_score = (
                interests_similarity * 0.5 +  # 50% weight to research interests
                education_similarity * 0.2 +  # 20% weight to education
                publications_similarity * 0.1 +  # 10% weight to publications
                keyword_match * 0.2  # 20% weight to keyword matching
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
                'keyword_match': round(keyword_match, 2),
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
    # Note: Pass use_transformer=False if you don't have GPU or adequate memory
    matcher = ResumeMatcher(use_transformer=True, use_spacy=True)
    matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)
    
    # Print results
    for i, match in enumerate(matches, 1):
        print(f"\nMatch #{i}: {match['name']} ({match['university']})")
        print(f"Overall Score: {match['overall_score']}")
        print(f"Research Interests Similarity: {match['interests_similarity']}")
        print(f"Education Similarity: {match['education_similarity']}")
        print(f"Publications Similarity: {match['publications_similarity']}")
        print(f"Keyword Match: {match['keyword_match']}")

if __name__ == "__main__":
    main()
