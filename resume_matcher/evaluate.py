"""
Evaluation module for matcher algorithms

This module provides utilities to evaluate and compare different matching algorithms
using standard information retrieval metrics.
"""

import numpy as np
import logging
from sklearn.metrics import ndcg_score
from matcher import ResumeMatcher
from enhanced_matcher import EnhancedMatcher
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_precision_at_k(relevance, k=5):
    """
    Calculate Precision@k metric.
    
    Args:
        relevance (list): Binary relevance scores (1 for relevant, 0 for not)
        k (int): Number of results to consider
        
    Returns:
        float: Precision@k score
    """
    if not relevance or k <= 0:
        return 0.0
    
    # Only consider top k results
    relevance = relevance[:k]
    
    # Calculate precision
    return sum(relevance) / min(k, len(relevance))

def calculate_average_precision(relevance):
    """
    Calculate Average Precision (AP) metric.
    
    Args:
        relevance (list): Binary relevance scores (1 for relevant, 0 for not)
        
    Returns:
        float: Average Precision score
    """
    if not relevance or sum(relevance) == 0:
        return 0.0
    
    # Calculate cumulative precision at each relevant position
    precision_sum = 0.0
    relevant_count = 0
    
    for i, rel in enumerate(relevance):
        if rel > 0:
            relevant_count += 1
            precision_at_i = sum(relevance[:i+1]) / (i + 1)
            precision_sum += precision_at_i
    
    # Calculate average precision
    return precision_sum / relevant_count if relevant_count > 0 else 0.0

def calculate_ndcg_at_k(relevance_scores, k=5):
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG) metric.
    
    Args:
        relevance_scores (list): Graded relevance scores (0-3 scale)
        k (int): Number of results to consider
        
    Returns:
        float: NDCG score
    """
    if not relevance_scores or k <= 0:
        return 0.0
    
    # Convert to numpy array for sklearn
    y_true = np.array([relevance_scores])
    y_pred = np.array([np.arange(len(relevance_scores), 0, -1)])
    
    # Calculate NDCG
    try:
        return ndcg_score(y_true, y_pred, k=min(k, len(relevance_scores)))
    except Exception as e:
        logger.error(f"Error calculating NDCG: {str(e)}")
        return 0.0

def calculate_diversity(matches, key='department'):
    """
    Calculate diversity of recommendations based on a specific attribute.
    
    Args:
        matches (list): List of match results
        key (str): Attribute to measure diversity on
        
    Returns:
        float: Diversity score (0-1)
    """
    if not matches:
        return 0.0
    
    # Extract values for the specified key
    values = [match.get(key, '') for match in matches]
    
    # Count unique values
    unique_values = set(values)
    
    # Calculate diversity as ratio of unique values to total
    return len(unique_values) / len(values)

def evaluate_matcher(matcher, test_data, ground_truth, top_k=5):
    """
    Evaluate a matcher algorithm on test data with ground truth.
    
    Args:
        matcher: Matcher instance to evaluate
        test_data (list): List of test cases (resume data and faculty profiles)
        ground_truth (list): List of ground truth relevant faculty IDs for each test case
        top_k (int): Number of top results to consider
        
    Returns:
        dict: Evaluation metrics
    """
    precision_scores = []
    average_precision_scores = []
    ndcg_scores = []
    diversity_scores = []
    execution_times = []
    
    for i, (resume, faculty_profiles) in enumerate(test_data):
        # Measure execution time
        start_time = time.time()
        matches = matcher.match_resume_with_faculty(resume, faculty_profiles)
        end_time = time.time()
        execution_times.append(end_time - start_time)
        
        # Get faculty IDs from top matches
        top_matches = matches[:top_k]
        matched_ids = [match['faculty_id'] for match in top_matches]
        
        # Calculate binary relevance (1 if faculty ID is in ground truth, 0 otherwise)
        binary_relevance = [1 if f_id in ground_truth[i] else 0 for f_id in matched_ids]
        
        # Calculate graded relevance (3 for perfect match, 2 for strong match, 1 for weak match)
        graded_relevance = []
        for f_id in matched_ids:
            if f_id in ground_truth[i].get('perfect', []):
                graded_relevance.append(3)
            elif f_id in ground_truth[i].get('strong', []):
                graded_relevance.append(2)
            elif f_id in ground_truth[i].get('weak', []):
                graded_relevance.append(1)
            else:
                graded_relevance.append(0)
        
        # Calculate metrics
        precision = calculate_precision_at_k(binary_relevance, top_k)
        average_precision = calculate_average_precision(binary_relevance)
        ndcg = calculate_ndcg_at_k(graded_relevance, top_k)
        diversity = calculate_diversity(top_matches)
        
        # Add to lists
        precision_scores.append(precision)
        average_precision_scores.append(average_precision)
        ndcg_scores.append(ndcg)
        diversity_scores.append(diversity)
    
    # Calculate aggregate metrics
    results = {
        'precision_at_k': np.mean(precision_scores),
        'mean_average_precision': np.mean(average_precision_scores),
        'ndcg_at_k': np.mean(ndcg_scores),
        'diversity': np.mean(diversity_scores),
        'average_execution_time': np.mean(execution_times),
        'num_test_cases': len(test_data)
    }
    
    return results

def compare_matchers(test_data, ground_truth, top_k=5):
    """
    Compare base and enhanced matcher algorithms.
    
    Args:
        test_data (list): List of test cases (resume data and faculty profiles)
        ground_truth (list): List of ground truth relevant faculty IDs for each test case
        top_k (int): Number of top results to consider
        
    Returns:
        dict: Comparison of evaluation metrics
    """
    # Initialize matchers
    base_matcher = ResumeMatcher(use_transformer=False, use_spacy=True)
    enhanced_matcher = EnhancedMatcher(use_transformer=False, use_spacy=True)
    
    # Evaluate base matcher
    logger.info("Evaluating base matcher...")
    base_results = evaluate_matcher(base_matcher, test_data, ground_truth, top_k)
    
    # Evaluate enhanced matcher
    logger.info("Evaluating enhanced matcher...")
    enhanced_results = evaluate_matcher(enhanced_matcher, test_data, ground_truth, top_k)
    
    # Compare results
    comparison = {
        'base_matcher': base_results,
        'enhanced_matcher': enhanced_results,
        'improvement': {
            'precision_at_k': enhanced_results['precision_at_k'] - base_results['precision_at_k'],
            'mean_average_precision': enhanced_results['mean_average_precision'] - base_results['mean_average_precision'],
            'ndcg_at_k': enhanced_results['ndcg_at_k'] - base_results['ndcg_at_k'],
            'diversity': enhanced_results['diversity'] - base_results['diversity'],
            'execution_time_change': enhanced_results['average_execution_time'] - base_results['average_execution_time']
        }
    }
    
    return comparison

def generate_test_data():
    """
    Generate synthetic test data for evaluation.
    
    Returns:
        tuple: (test_data, ground_truth)
    """
    # Create test resumes
    resumes = [
        {
            'name': 'Student 1',
            'research_interests': [
                'Machine Learning',
                'Deep Learning',
                'Computer Vision'
            ],
            'education': [
                {
                    'degree': 'MS',
                    'field': 'Computer Science',
                    'institution': 'Stanford University',
                    'year': 2023
                }
            ]
        },
        {
            'name': 'Student 2',
            'research_interests': [
                'Natural Language Processing',
                'Information Retrieval',
                'Text Mining'
            ],
            'education': [
                {
                    'degree': 'BS',
                    'field': 'Computer Science',
                    'institution': 'MIT',
                    'year': 2022
                }
            ]
        },
        {
            'name': 'Student 3',
            'research_interests': [
                'Robotics',
                'Computer Vision',
                'Control Systems'
            ],
            'education': [
                {
                    'degree': 'MS',
                    'field': 'Electrical Engineering',
                    'institution': 'UC Berkeley',
                    'year': 2023
                }
            ]
        }
    ]
    
    # Create faculty profiles
    faculty_profiles = [
        {
            'faculty_id': 1,
            'name': 'Dr. Alice Smith',
            'department_name': 'Computer Science',
            'university_name': 'Stanford University',
            'research_interests': [
                'Machine Learning',
                'Deep Neural Networks',
                'Computer Vision',
                'AI Ethics'
            ],
            'education': [
                {
                    'degree': 'PhD',
                    'field': 'Computer Science',
                    'institution': 'MIT',
                    'year': 2010
                }
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
                'Sensor Networks',
                'Autonomous Systems'
            ],
            'education': [
                {
                    'degree': 'PhD',
                    'field': 'Electrical Engineering',
                    'institution': 'Stanford University',
                    'year': 2008
                }
            ],
            'funding': [
                {'title': 'Advanced Computer Vision Research', 'amount': 1500000, 'active': True},
                {'title': 'Robotics Initiative', 'amount': 750000, 'active': True}
            ]
        },
        {
            'faculty_id': 3,
            'name': 'Dr. Carol Williams',
            'department_name': 'Computer Science',
            'university_name': 'UC Berkeley',
            'research_interests': [
                'Natural Language Processing',
                'Machine Translation',
                'Information Extraction'
            ],
            'education': [
                {
                    'degree': 'PhD',
                    'field': 'Linguistics',
                    'institution': 'Stanford University',
                    'year': 2012
                }
            ],
            'citation_metrics': {
                'h_index': 18,
                'total_citations': 3200
            }
        },
        {
            'faculty_id': 4,
            'name': 'Dr. David Lee',
            'department_name': 'Computer Science',
            'university_name': 'Stanford University',
            'research_interests': [
                'Reinforcement Learning',
                'Game Theory',
                'Multi-agent Systems'
            ],
            'education': [
                {
                    'degree': 'PhD',
                    'field': 'Computer Science',
                    'institution': 'UC Berkeley',
                    'year': 2011
                }
            ]
        },
        {
            'faculty_id': 5,
            'name': 'Dr. Emily Chen',
            'department_name': 'Electrical Engineering',
            'university_name': 'UC Berkeley',
            'research_interests': [
                'Computer Vision',
                'Robotics',
                'Medical Imaging'
            ],
            'education': [
                {
                    'degree': 'PhD',
                    'field': 'Electrical Engineering',
                    'institution': 'MIT',
                    'year': 2014
                }
            ],
            'awards': [
                'NSF CAREER Award',
                'Outstanding Young Researcher'
            ]
        }
    ]
    
    # Create test data (each resume paired with all faculty profiles)
    test_data = [(resume, faculty_profiles) for resume in resumes]
    
    # Create ground truth (faculty IDs that are relevant for each resume)
    # Using graded relevance: perfect, strong, weak matches
    ground_truth = [
        {
            'perfect': [1],  # Dr. Alice Smith (ML, Computer Vision)
            'strong': [2],   # Dr. Bob Johnson (Computer Vision)
            'weak': [5]      # Dr. Emily Chen (Computer Vision)
        },
        {
            'perfect': [3],  # Dr. Carol Williams (NLP)
            'strong': [],
            'weak': [4]      # Dr. David Lee (somewhat related fields)
        },
        {
            'perfect': [2, 5],  # Dr. Bob Johnson & Dr. Emily Chen (Robotics, CV)
            'strong': [],
            'weak': [1]         # Dr. Alice Smith (Computer Vision)
        }
    ]
    
    return test_data, ground_truth

def main():
    """
    Run evaluation and comparison of matcher algorithms.
    """
    # Generate test data
    test_data, ground_truth = generate_test_data()
    
    # Compare matchers
    results = compare_matchers(test_data, ground_truth, top_k=3)
    
    # Print results
    print("\n===== Matcher Comparison Results =====")
    print("\nBase Matcher Metrics:")
    for metric, value in results['base_matcher'].items():
        print(f"  {metric}: {value:.4f}")
    
    print("\nEnhanced Matcher Metrics:")
    for metric, value in results['enhanced_matcher'].items():
        print(f"  {metric}: {value:.4f}")
    
    print("\nImprovement:")
    for metric, value in results['improvement'].items():
        print(f"  {metric}: {value:+.4f}")

if __name__ == "__main__":
    main()
