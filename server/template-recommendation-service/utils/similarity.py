import numpy as np
from typing import List, Set
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_processing import normalize_text, extract_keywords

def cosine_sim(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (0-1)
    """
    return cosine_similarity([vec1], [vec2])[0][0]

def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.
    
    Args:
        set1: First set
        set2: Second set
        
    Returns:
        Jaccard similarity (0-1)
    """
    if not set1 or not set2:
        return 0.0
        
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def keyword_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts based on shared keywords.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # Extract keywords
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    # Calculate Jaccard similarity
    return jaccard_similarity(keywords1, keywords2)

def industry_similarity(industry1: str, industries2: List[str]) -> float:
    """
    Calculate similarity between an industry and a list of industries.
    
    Args:
        industry1: Primary industry
        industries2: List of industries to compare against
        
    Returns:
        Similarity score (0-1)
    """
    if not industry1 or not industries2:
        return 0.0
    
    # Normalize
    industry1 = normalize_text(industry1)
    industries2 = [normalize_text(i) for i in industries2]
    
    # Check for exact match
    if industry1 in industries2:
        return 1.0
    
    # Check for partial matches
    partial_matches = [
        i for i in industries2 
        if industry1 in i or i in industry1
    ]
    
    if partial_matches:
        return 0.7  # High but not perfect score for partial matches
    
    # Check for keyword similarity with each industry
    similarities = [keyword_similarity(industry1, i) for i in industries2]
    return max(similarities) if similarities else 0.0