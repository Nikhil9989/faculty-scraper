# Resume-Faculty Matcher

A Python module for matching student resumes with faculty profiles using advanced NLP techniques and enhanced scoring algorithms to identify the most suitable research advisors.

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
- BM25 ranking for improved information retrieval
- Keyword extraction and matching for topic alignment

### Enhanced Scoring System (New!)
- Dynamic weight adjustment based on available data
- Domain-specific boosts for high-demand research areas
- Academic impact metrics (citation count, h-index)
- Award and recognition scoring
- Research funding evaluation
- Personalization options for individual preferences

### Intelligent Scoring
- Weighted scoring across multiple dimensions:
  - Research interests (dynamically weighted)
  - Education background
  - Publications
  - Keyword matching
  - Citation impact
  - Award recognition
  - Funding success
- Normalized scoring between 0 and 1 for easy interpretation
- Smart fallback mechanisms when certain data points are missing

### Advanced Text Processing
- Lemmatization to normalize word forms
- Stopword removal to focus on meaningful content
- Entity recognition for identifying research domains
- Named entity recognition for organizations and specialized terms

### Evaluation Framework (New!)
- Standard IR metrics (Precision@k, MAP, NDCG)
- Diversity measurement
- Performance benchmarking
- Automated test data generation

## Usage

### Basic Matcher
```python
from matcher import ResumeMatcher

# Create basic matcher instance
matcher = ResumeMatcher(use_transformer=True, use_spacy=True)

# Get matches
matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)
```

### Enhanced Matcher with Personalization
```python
from enhanced_matcher import EnhancedMatcher

# Create enhanced matcher with personalized weights
matcher = EnhancedMatcher(use_transformer=True, use_spacy=True)
matcher.set_personalization(
    interests_weight=0.6,
    education_weight=0.2,
    keywords_weight=0.2,
    citation_weight=0.1,
    awards_weight=0.05,
    grants_weight=0.05
)

# Get enhanced matches
matches = matcher.match_resume_with_faculty(resume_data, faculty_profiles)

# Display top matches
for i, match in enumerate(matches[:3], 1):
    print(f"{i}. {match['name']} - Score: {match['overall_score']}")
    print(f"   Research Match: {match['interests_similarity']}")
    print(f"   Domain Boost: {match['domain_boost']}")
    
    # Additional metrics in enhanced matcher
    if match['citation_impact'] > 0:
        print(f"   Citation Impact: {match['citation_impact']}")
    if match['award_recognition'] > 0:
        print(f"   Award Recognition: {match['award_recognition']}")
    if match['funding_score'] > 0:
        print(f"   Funding Score: {match['funding_score']}")
```

### Evaluation
```python
from evaluate import compare_matchers, generate_test_data

# Generate test data and ground truth
test_data, ground_truth = generate_test_data()

# Compare base and enhanced matchers
results = compare_matchers(test_data, ground_truth, top_k=3)

# Print improvement metrics
for metric, value in results['improvement'].items():
    print(f"{metric}: {value:+.4f}")
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
- Rank-BM25: For BM25 ranking algorithm

## Configuration

The matcher can be configured for different environments:

```python
# Full NLP capabilities (requires more memory)
matcher = EnhancedMatcher(use_transformer=True, use_spacy=True)

# Lighter version for systems with limited resources
matcher = EnhancedMatcher(use_transformer=False, use_spacy=True)

# Basic version with just TF-IDF and BM25 (minimal requirements)
matcher = EnhancedMatcher(use_transformer=False, use_spacy=False)
```

## Future Enhancements

- Machine learning models trained on successful advisor-student pairs
- Citation network analysis for publication importance
- Academic genealogy exploration for academic "fit"
- Integration with faculty recommendation letters and success rates
- Learning-to-rank implementation for optimal ordering
