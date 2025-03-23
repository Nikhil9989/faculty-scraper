# Resume-Faculty Matcher

A Python module for matching student resumes with faculty profiles using advanced NLP techniques to identify the most suitable research advisors.

## Overview

This component provides sophisticated algorithms to:
- Compare student research interests with faculty research areas using semantic similarity
- Extract and match keywords from research descriptions
- Calculate similarity scores using multiple NLP techniques
- Rank faculty members based on compatibility with student interests
- Generate match recommendations to help students find potential advisors

## Features

### Multiple Similarity Methods
- TF-IDF and cosine similarity for text comparison
- BERT-based semantic similarity using Sentence Transformers
- spaCy-based document similarity with word vectors
- Keyword extraction and matching for topic alignment

### Intelligent Scoring
- Weighted scoring across multiple dimensions:
  - Research interests (50% weight)
  - Education background (20% weight)
  - Publications (10% weight)
  - Keyword matching (20% weight)
- Normalized scoring between 0 and 1 for easy interpretation
- Smart fallback mechanisms when certain data points are missing

### Advanced Text Processing
- Lemmatization to normalize word forms
- Stopword removal to focus on meaningful content
- Entity recognition for identifying research domains
- Named entity recognition for organizations and specialized terms

## Usage

```python
from matcher import ResumeMatcher

# Create matcher instance with advanced NLP
matcher = ResumeMatcher(use_transformer=True, use_spacy=True)

# Resume data (from parsing)
resume_data = {
    'name': 'John Doe',
    'research_interests': ['Machine Learning', 'Computer Vision'],
    'education': [
        {
            'degree': 'MS',
            'field': 'Computer Science', 
            'institution': 'Stanford',
            'year': 2023
        }
    ]
}

# Faculty profiles (from database)
faculty_profiles = [
    {
        'faculty_id': 1,
        'name': 'Dr. Smith',
        'department_name': 'Computer Science',
        'university_name': 'MIT',
        'research_interests': ['Machine Learning', 'AI Ethics']
    },
    # More faculty profiles...
]

# Get ranked matches
matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)

# Display top matches
for i, match in enumerate(matches[:3], 1):
    print(f"{i}. {match['name']} - Score: {match['overall_score']}")
    print(f"   Research Match: {match['interests_similarity']}")
    print(f"   Keyword Match: {match['keyword_match']}")
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

## Dependencies

- NumPy & SciPy: For numerical operations
- scikit-learn: For TF-IDF vectorization and cosine similarity
- spaCy: For word vectors and NLP processing
- NLTK: For text tokenization and basic NLP
- Sentence Transformers: For BERT-based semantic similarity

## Configuration

The matcher can be configured for different environments:

```python
# Full NLP capabilities (requires more memory)
matcher = ResumeMatcher(use_transformer=True, use_spacy=True)

# Lighter version for systems with limited resources
matcher = ResumeMatcher(use_transformer=False, use_spacy=True)

# Basic version with just TF-IDF (minimal requirements)
matcher = ResumeMatcher(use_transformer=False, use_spacy=False)
```

## Future Enhancements

- Machine learning models trained on successful advisor-student pairs
- Citation network analysis for publication importance
- Evaluation metrics to measure recommendation quality
- Research domain-specific matching techniques
