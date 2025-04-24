import re
from typing import List, Set

def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace, converting to lowercase, etc.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text
    
def extract_keywords(text: str, stop_words: Set[str] = None) -> List[str]:
    """
    Extract keywords from text by removing stop words and keeping only nouns and adjectives.
    This is a simple implementation without using NLP libraries.
    
    Args:
        text: Input text
        stop_words: Set of stop words to remove
        
    Returns:
        List of keywords
    """
    if not text:
        return []
        
    if stop_words is None:
        # Common English stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
            'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
            'to', 'from', 'in', 'on', 'by', 'with', 'at', 'be', 'have', 'has', 'had',
            'do', 'does', 'did', 'are', 'am', 'was', 'were', 'being', 'been', 'can',
            'could', 'will', 'would', 'should', 'may', 'might', 'must', 'shall', 'i',
            'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself', 'he',
            'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
            'itself', 'we', 'us', 'our', 'ours', 'ourselves', 'they', 'them', 'their',
            'theirs', 'themselves', 'who', 'whom', 'whose', 'when', 'where', 'why',
            'how', 'all', 'any', 'some', 'many', 'each', 'every', 'few', 'more',
            'most', 'other', 'another', 'no', 'not', 'only', 'own', 'same', 'too',
            'very', 'yeah', 'yes', 'no', 'sure', 'well'
        }
    
    # Normalize text
    text = normalize_text(text)
    
    # Split into words
    words = text.split()
    
    # Filter out stop words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Remove duplicates while preserving order
    seen = set()
    return [word for word in keywords if not (word in seen or seen.add(word))]