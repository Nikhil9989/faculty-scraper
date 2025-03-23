"""
Enhanced Resume-Faculty Matching Algorithm with Advanced Scoring

This module extends the basic matcher with:
1. Dynamic weight adjustment based on data quality
2. Domain-specific scoring boosts
3. Enhanced scoring mechanisms (BM25, TF-IDF+, citation analysis)
4. Personalization options
"""

import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi
from collections import Counter
import re
from matcher import ResumeMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedMatcher(ResumeMatcher):
    """
    An enhanced matcher with improved scoring mechanisms for better faculty-resume matching.
    Extends the base ResumeMatcher with advanced ranking features.
    """
    
    def __init__(self, use_transformer=True, use_spacy=True):
        """
        Initialize the EnhancedMatcher with NLP models and additional scoring options.
        
        Args:
            use_transformer (bool): Whether to use BERT transformer models
            use_spacy (bool): Whether to use spaCy for entity extraction
        """
        super().__init__(use_transformer, use_spacy)
        
        # Domain-specific boosts (research areas that get a bonus in matching)
        # These reflect current high-demand research areas
        self.domain_boosts = {
            'machine learning': 1.2,
            'artificial intelligence': 1.2,
            'deep learning': 1.2,
            'natural language processing': 1.15,
            'computer vision': 1.15,
            'reinforcement learning': 1.15,
            'robotics': 1.1,
            'data mining': 1.1,
            'data science': 1.1,
            'cybersecurity': 1.1,
            'blockchain': 1.1,
            'quantum computing': 1.2
        }
        
        # Default personalization settings (can be modified per request)
        self.personalization = {
            'interests_weight': 0.5,
            'education_weight': 0.2,
            'publications_weight': 0.1,
            'keywords_weight': 0.2,
            # Optional weights
            'citation_weight': 0.0,  # Weight for citation metrics if available
            'awards_weight': 0.0,    # Weight for awards/recognition if available
            'grants_weight': 0.0     # Weight for grant funding if available
        }
        
        # Initialize BM25 for research interest matching
        # (will be populated during matching)
        self.bm25 = None
    
    def set_personalization(self, **kwargs):
        """
        Set personalization weights for different matching factors.
        
        Args:
            **kwargs: Key-value pairs for personalization settings
            
        Returns:
            self: For method chaining
        """
        for key, value in kwargs.items():
            if key in self.personalization:
                self.personalization[key] = value
        
        # Normalize weights to ensure they sum to 1.0
        weight_sum = sum(self.personalization.values())
        if weight_sum > 0:
            for key in self.personalization:
                self.personalization[key] /= weight_sum
        
        return self
    
    def calculate_citation_impact(self, faculty):
        """
        Calculate impact score based on citation metrics if available.
        
        Args:
            faculty (dict): Faculty profile with citation info
            
        Returns:
            float: Citation impact score between 0 and 1
        """
        if 'citation_metrics' not in faculty:
            return 0.0
        
        metrics = faculty['citation_metrics']
        
        # Calculate based on h-index and citation count if available
        h_index = metrics.get('h_index', 0)
        total_citations = metrics.get('total_citations', 0)
        
        # Simple formula giving more weight to h-index than raw citation count
        # These thresholds can be adjusted based on field norms
        h_index_score = min(h_index / 40.0, 1.0)  # Normalize h-index (40+ is top tier)
        citation_score = min(total_citations / 10000.0, 1.0)  # Normalize citations
        
        # Combine scores (70% h-index, 30% citations)
        impact_score = 0.7 * h_index_score + 0.3 * citation_score
        
        return impact_score
    
    def calculate_award_recognition(self, faculty):
        """
        Calculate recognition score based on awards and honors.
        
        Args:
            faculty (dict): Faculty profile with awards info
            
        Returns:
            float: Recognition score between 0 and 1
        """
        if 'awards' not in faculty or not faculty['awards']:
            return 0.0
        
        awards = faculty['awards']
        
        # Award tiers (can be expanded)
        prestigious_awards = [
            'turing', 'nobel', 'fields medal', 'national academy', 
            'acm fellow', 'ieee fellow', 'nsf career'
        ]
        
        major_awards = [
            'best paper', 'distinguished', 'outstanding', 'excellence',
            'research award', 'teaching award'
        ]
        
        # Count awards by prestige
        prestigious_count = sum(1 for award in awards if any(
            term.lower() in award.lower() for term in prestigious_awards
        ))
        
        major_count = sum(1 for award in awards if any(
            term.lower() in award.lower() for term in major_awards
        ))
        
        other_count = len(awards) - prestigious_count - major_count
        
        # Calculate weighted score
        award_score = (prestigious_count * 0.5 + major_count * 0.3 + other_count * 0.1) / max(len(awards), 1)
        award_score = min(award_score, 1.0)  # Cap at 1.0
        
        return award_score
    
    def calculate_funding_score(self, faculty):
        """
        Calculate score based on research funding if available.
        
        Args:
            faculty (dict): Faculty profile with funding info
            
        Returns:
            float: Funding score between 0 and 1
        """
        if 'funding' not in faculty or not faculty['funding']:
            return 0.0
        
        funding = faculty['funding']
        
        # Get total funding amount and number of grants
        total_amount = sum(grant.get('amount', 0) for grant in funding)
        grant_count = len(funding)
        
        # Active grants are more valuable
        active_grants = sum(1 for grant in funding if grant.get('active', False))
        
        # Calculate score based on funding amount (with cap at $5M)
        amount_score = min(total_amount / 5000000.0, 1.0)
        
        # Calculate score based on grant count (with cap at 10 grants)
        count_score = min(grant_count / 10.0, 1.0)
        
        # Calculate score based on active grants (with cap at 5 active grants)
        active_score = min(active_grants / 5.0, 1.0)
        
        # Combine scores
        funding_score = 0.4 * amount_score + 0.3 * count_score + 0.3 * active_score
        
        return funding_score
    
    def calculate_domain_boost(self, faculty_interests):
        """
        Calculate domain-specific boost based on high-demand research areas.
        
        Args:
            faculty_interests (list): Faculty research interests
            
        Returns:
            float: Boost factor between 1.0 and 1.2
        """
        if not faculty_interests:
            return 1.0
        
        # Join interests into a single text
        interests_text = " ".join(str(i).lower() for i in faculty_interests)
        
        # Calculate maximum boost from any matching domain
        max_boost = 1.0
        for domain, boost in self.domain_boosts.items():
            if domain in interests_text:
                max_boost = max(max_boost, boost)
        
        return max_boost
    
    def calculate_bm25_similarity(self, query_tokens, all_doc_tokens):
        """
        Calculate BM25 similarity score between query and document.
        
        Args:
            query_tokens (list): List of tokens from the query
            all_doc_tokens (list): List of lists of tokens from documents
            
        Returns:
            float: Normalized BM25 score
        """
        if not query_tokens or not all_doc_tokens:
            return 0.0
        
        # Create BM25 model
        bm25 = BM25Okapi(all_doc_tokens)
        
        # Calculate scores
        scores = bm25.get_scores(query_tokens)
        
        if len(scores) < 1:
            return 0.0
        
        # Return normalized score for the first document
        # (Normalize by max score to get a value between 0 and 1)
        max_score = max(scores) if max(scores) > 0 else 1.0
        return scores[0] / max_score
    
    def tokenize_text(self, text):
        """
        Tokenize text into words for BM25 indexing.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of tokens
        """
        if not text:
            return []
        
        # Convert to lowercase and split on non-alphanumeric characters
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        
        # Remove single character tokens and common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of'}
        tokens = [t for t in tokens if len(t) > 1 and t not in stopwords]
        
        return tokens
    
    def dynamic_weight_adjustment(self, resume_data, faculty):
        """
        Dynamically adjust weights based on data availability and quality.
        
        Args:
            resume_data (dict): Resume data
            faculty (dict): Faculty profile
            
        Returns:
            dict: Adjusted weights
        """
        # Start with personalization weights
        weights = self.personalization.copy()
        
        # Factors to consider for adjustment
        has_research_interests = bool(resume_data.get('research_interests')) and bool(faculty.get('research_interests'))
        has_education = bool(resume_data.get('education')) and bool(faculty.get('education'))
        has_publications = bool(resume_data.get('publications')) and bool(faculty.get('publications'))
        
        # If some data is missing, redistribute weights
        if not has_research_interests:
            # Remove research interests weight and redistribute
            interests_weight = weights['interests_weight']
            weights['interests_weight'] = 0.0
            
            # Redistribute to other available factors
            available_factors = []
            if has_education:
                available_factors.append('education_weight')
            if has_publications:
                available_factors.append('publications_weight')
            
            # Always include keywords as fallback
            available_factors.append('keywords_weight')
            
            # Redistribute weight
            for factor in available_factors:
                weights[factor] += interests_weight / len(available_factors)
        
        # Similar adjustments for other missing factors
        if not has_education and weights['education_weight'] > 0:
            edu_weight = weights['education_weight']
            weights['education_weight'] = 0.0
            
            # Boost interests and keywords
            weights['interests_weight'] += edu_weight * 0.7
            weights['keywords_weight'] += edu_weight * 0.3
        
        # Normalize weights
        weight_sum = sum(weights.values())
        if weight_sum > 0:
            for key in weights:
                weights[key] /= weight_sum
        
        return weights
    
    def match_resume_with_faculty(self, resume_data, faculty_profiles, personalization=None):
        """
        Match a resume with multiple faculty profiles using enhanced scoring.
        
        Args:
            resume_data (dict): Parsed resume data with research interests
            faculty_profiles (list): List of faculty profile dictionaries
            personalization (dict, optional): Custom weights for different factors
            
        Returns:
            list: Ranked list of faculty matches with similarity scores
        """
        # Apply personalization if provided
        if personalization:
            self.set_personalization(**personalization)
        
        matches = []
        
        # Extract resume research interests
        resume_interests = resume_data.get('research_interests', [])
        resume_interests_text = " ".join(str(interest) for interest in resume_interests)
        
        # Tokenize resume interests for BM25
        resume_interests_tokens = self.tokenize_text(resume_interests_text)
        
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
            
            # Dynamically adjust weights based on available data
            weights = self.dynamic_weight_adjustment(resume_data, faculty)
            
            # Tokenize faculty interests for BM25
            faculty_interests_tokens = self.tokenize_text(faculty_interests_text)
            
            # Calculate research interest similarity using multiple methods
            # 1. TF-IDF + Transformer + spaCy similarity
            interests_nlp_similarity = self.calculate_combined_similarity(
                resume_interests_text, faculty_interests_text
            )
            
            # 2. BM25 similarity
            bm25_score = 0.0
            if resume_interests_tokens and faculty_interests_tokens:
                bm25_score = self.calculate_bm25_similarity(
                    resume_interests_tokens, [faculty_interests_tokens]
                )
            
            # Combine NLP and BM25 scores for research interests
            interests_similarity = 0.7 * interests_nlp_similarity + 0.3 * bm25_score
            
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
            keyword_match = 0.0
            if resume_interests_text and faculty_interests_text:
                resume_keywords = self.extract_keywords(resume_interests_text)
                faculty_keywords = self.extract_keywords(faculty_interests_text)
                
                # Calculate keyword overlap
                if resume_keywords and faculty_keywords:
                    common_keywords = set(k.lower() for k in resume_keywords) & set(k.lower() for k in faculty_keywords)
                    keyword_match = len(common_keywords) / max(len(resume_keywords), 1)
            
            # Calculate additional impact scores if available
            citation_impact = self.calculate_citation_impact(faculty)
            award_recognition = self.calculate_award_recognition(faculty)
            funding_score = self.calculate_funding_score(faculty)
            
            # Apply domain boost for high-demand fields
            domain_boost = self.calculate_domain_boost(faculty_interests)
            
            # Calculate weighted overall score using dynamically adjusted weights
            overall_score = (
                interests_similarity * weights['interests_weight'] +
                education_similarity * weights['education_weight'] +
                publications_similarity * weights['publications_weight'] +
                keyword_match * weights['keywords_weight'] +
                citation_impact * weights.get('citation_weight', 0.0) +
                award_recognition * weights.get('awards_weight', 0.0) +
                funding_score * weights.get('grants_weight', 0.0)
            )
            
            # Apply domain boost
            overall_score *= domain_boost
            
            # Cap at 1.0
            overall_score = min(overall_score, 1.0)
            
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
                'citation_impact': round(citation_impact, 2),
                'award_recognition': round(award_recognition, 2),
                'funding_score': round(funding_score, 2),
                'domain_boost': round(domain_boost, 2),
                'overall_score': round(overall_score, 2)
            })
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matches

def main():
    """
    Example usage of the EnhancedMatcher class.
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
            ],
            'citation_metrics': {
                'h_index': 25,
                'total_citations': 5000
            },
            'awards': [
                'ACM Distinguished Scientist',
                'Outstanding Teaching Award'
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
            ],
            'funding': [
                {'title': 'Advanced Computer Vision Research', 'amount': 1500000, 'active': True},
                {'title': 'Robotics Initiative', 'amount': 750000, 'active': True}
            ]
        }
    ]
    
    # Create matcher with personalized weights
    personalization = {
        'interests_weight': 0.6,
        'education_weight': 0.2,
        'keywords_weight': 0.2,
        'citation_weight': 0.1,  # Add some weight to citations
        'awards_weight': 0.05,   # Add weight to awards
        'grants_weight': 0.05    # Add weight to grants
    }
    
    matcher = EnhancedMatcher(use_transformer=False, use_spacy=True)  # Set use_transformer=True if GPU available
    matcher.set_personalization(**personalization)
    
    matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)
    
    # Print results
    for i, match in enumerate(matches, 1):
        print(f"\nMatch #{i}: {match['name']} ({match['university']})")
        print(f"Overall Score: {match['overall_score']}")
        print(f"Research Interests Similarity: {match['interests_similarity']}")
        print(f"Education Similarity: {match['education_similarity']}")
        print(f"Keyword Match: {match['keyword_match']}")
        if match['citation_impact'] > 0:
            print(f"Citation Impact: {match['citation_impact']}")
        if match['award_recognition'] > 0:
            print(f"Award Recognition: {match['award_recognition']}")
        if match['funding_score'] > 0:
            print(f"Funding Score: {match['funding_score']}")
        print(f"Domain Boost: {match['domain_boost']}")

if __name__ == "__main__":
    main()
