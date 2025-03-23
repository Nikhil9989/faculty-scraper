# Resume-Faculty Matcher

A Python module for matching student resumes with faculty profiles based on research interests, education, and other criteria.

## Overview

This component provides algorithms to:
- Compare student research interests with faculty research areas
- Calculate similarity scores between resumes and faculty profiles
- Rank faculty members based on compatibility with student interests
- Generate match recommendations to help students find potential advisors

## Features

- TF-IDF and cosine similarity for text comparison
- Weighted scoring across multiple dimensions:
  - Research interests (70% weight)
  - Education background (20% weight)
  - Publications (10% weight)
- Normalized scoring between 0 and 1 for easy interpretation

## Usage

```python
from matcher import ResumeMatcher

# Create matcher instance
matcher = ResumeMatcher()

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
```

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- NumPy: For numerical operations
- scikit-learn: For TF-IDF vectorization and cosine similarity
- SciPy: Used by scikit-learn for sparse matrix operations

## Future Enhancements

- Implementation of more advanced NLP techniques
- Better scoring algorithms with machine learning
- Integration with academic paper databases for publication analysis
