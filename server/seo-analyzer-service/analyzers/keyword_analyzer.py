import spacy
from collections import Counter, defaultdict
from typing import List, Dict, Set, Optional
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class KeywordAnalyzer:
    """Analyze keywords and find opportunities."""
    
    def __init__(self, nlp=None):
        self.nlp = nlp or spacy.load("en_core_web_sm")
        self.stop_words = self.nlp.Defaults.stop_words
    
    def find_opportunities(self, content: str, target_keywords: List[str]) -> Dict:
        """Find keyword opportunities in content."""
        doc = self.nlp(content)
        
        # Extract existing keywords
        existing_keywords = self.extract_keywords(doc)
        
        # Find semantic variations
        semantic_variations = self.find_semantic_variations(target_keywords, existing_keywords)
        
        # Find long-tail opportunities
        long_tail_opportunities = self.find_long_tail_keywords(doc, target_keywords)
        
        # Find question-based keywords
        question_keywords = self.find_question_keywords(doc)
        
        # Find trending topics (simplified)
        trending_topics = self.find_trending_topics(doc)
        
        # Calculate keyword gaps
        keyword_gaps = self.identify_keyword_gaps(target_keywords, existing_keywords)
        
        return {
            'existing_keywords': existing_keywords,
            'semantic_variations': semantic_variations,
            'long_tail_opportunities': long_tail_opportunities,
            'question_keywords': question_keywords,
            'trending_topics': trending_topics,
            'keyword_gaps': keyword_gaps
        }
    
    def extract_keywords(self, doc) -> Dict[str, float]:
        """Extract keywords from document with TF-IDF scores."""
        # Simple keyword extraction using noun chunks and named entities
        keywords = []
        
        # Add noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1 and not all(token.is_stop for token in chunk):
                keywords.append(chunk.text.lower())
        
        # Add named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART", "EVENT"]:
                keywords.append(ent.text.lower())
        
        # Calculate frequency
        keyword_freq = Counter(keywords)
        total = sum(keyword_freq.values())
        
        return {k: v/total for k, v in keyword_freq.most_common(20)}
    
    def find_semantic_variations(self, target_keywords: List[str], existing_keywords: Dict[str, float]) -> Dict[str, List[str]]:
        """Find semantic variations of target keywords."""
        variations = {}
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            related = []
            
            # Find similar existing keywords
            for existing in existing_keywords:
                if self.is_semantically_related(keyword_lower, existing):
                    related.append(existing)
            
            # Generate variations
            variations[keyword] = related + self.generate_variations(keyword)
        
        return variations
    
    def is_semantically_related(self, word1: str, word2: str) -> bool:
        """Check if two words are semantically related."""
        # Simple check: common words or substring match
        words1 = set(word1.split())
        words2 = set(word2.split())
        
        # Check for common words
        if words1.intersection(words2):
            return True
        
        # Check for substring match
        if word1 in word2 or word2 in word1:
            return True
        
        return False
    
    def generate_variations(self, keyword: str) -> List[str]:
        """Generate variations of a keyword."""
        variations = []
        
        # Add plural/singular forms
        if keyword.endswith('s'):
            variations.append(keyword[:-1])
        else:
            variations.append(keyword + 's')
        
        # Add common prefixes/suffixes
        prefixes = ['best', 'top', 'free', 'cheap', 'professional']
        suffixes = ['services', 'solutions', 'tools', 'software', 'platform']
        
        for prefix in prefixes:
            variations.append(f"{prefix} {keyword}")
        
        for suffix in suffixes:
            if not keyword.endswith(suffix):
                variations.append(f"{keyword} {suffix}")
        
        return variations
    
    def find_long_tail_keywords(self, doc, target_keywords: List[str]) -> List[str]:
        """Find long-tail keyword opportunities."""
        long_tail = []
        
        # Extract 3-5 word phrases
        for i in range(len(doc) - 4):
            phrase = doc[i:i+5].text.lower()
            words = phrase.split()
            
            if 3 <= len(words) <= 5:
                # Check if contains target keyword
                for keyword in target_keywords:
                    if keyword.lower() in phrase:
                        if not any(token.is_stop or token.is_punct for token in doc[i:i+5]):
                            long_tail.append(phrase)
        
        return list(set(long_tail))
    
    def find_question_keywords(self, doc) -> List[str]:
        """Find question-based keywords."""
        questions = []
        question_words = ['who', 'what', 'where', 'when', 'why', 'how', 'which']
        
        for sent in doc.sents:
            if any(sent.text.lower().startswith(q) for q in question_words):
                questions.append(sent.text.strip())
        
        return questions
    
    def find_trending_topics(self, doc) -> List[str]:
        """Find potentially trending topics (simplified)."""
        # In a real implementation, this would connect to trend APIs
        # For now, we'll extract high-frequency noun phrases
        noun_phrases = []
        
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                noun_phrases.append(chunk.text.lower())
        
        phrase_freq = Counter(noun_phrases)
        return [phrase for phrase, count in phrase_freq.most_common(10) if count > 1]
    
    def identify_keyword_gaps(self, target_keywords: List[str], existing_keywords: Dict[str, float]) -> List[str]:
        """Identify keywords that should be used but aren't."""
        gaps = []
        existing_set = set(existing_keywords.keys())
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Check if keyword or its variations exist
            if keyword_lower not in existing_set:
                found_variation = False
                for existing in existing_set:
                    if self.is_semantically_related(keyword_lower, existing):
                        found_variation = True
                        break
                
                if not found_variation:
                    gaps.append(keyword)
        
        return gaps
    
    def research_keywords(self, seed_keywords: List[str], industry: Optional[str] = None) -> Dict:
        """Research keywords based on seed keywords."""
        # This is a simplified version. In production, you'd integrate with keyword research APIs
        
        related_keywords = {}
        keyword_ideas = []
        
        for seed in seed_keywords:
            # Generate variations
            variations = self.generate_variations(seed)
            related_keywords[seed] = variations
            
            # Generate keyword ideas
            if industry:
                industry_specific = self.generate_industry_keywords(seed, industry)
                keyword_ideas.extend(industry_specific)
        
        return {
            'seed_keywords': seed_keywords,
            'related_keywords': related_keywords,
            'keyword_ideas': list(set(keyword_ideas)),
            'search_volume_estimates': self.estimate_search_volume(seed_keywords + keyword_ideas),
            'competition_levels': self.estimate_competition(seed_keywords + keyword_ideas)
        }
    
    def generate_industry_keywords(self, seed: str, industry: str) -> List[str]:
        """Generate industry-specific keywords."""
        industry_modifiers = {
            'technology': ['software', 'app', 'platform', 'digital', 'AI', 'automation'],
            'healthcare': ['medical', 'health', 'clinic', 'patient', 'care', 'wellness'],
            'finance': ['financial', 'investment', 'banking', 'money', 'wealth', 'trading'],
            'ecommerce': ['online', 'shop', 'store', 'buy', 'purchase', 'shipping'],
            'education': ['learning', 'course', 'training', 'tutorial', 'education', 'study']
        }
        
        modifiers = industry_modifiers.get(industry.lower(), [])
        return [f"{seed} {modifier}" for modifier in modifiers]
    
    def estimate_search_volume(self, keywords: List[str]) -> Dict[str, str]:
        """Estimate search volume (simplified)."""
        # In production, this would use actual search volume data
        volumes = {}
        for keyword in keywords:
            word_count = len(keyword.split())
            if word_count == 1:
                volumes[keyword] = "High"
            elif word_count == 2:
                volumes[keyword] = "Medium"
            else:
                volumes[keyword] = "Low"
        return volumes
    
    def estimate_competition(self, keywords: List[str]) -> Dict[str, str]:
        """Estimate competition level (simplified)."""
        # In production, this would use actual competition data
        competition = {}
        for keyword in keywords:
            word_count = len(keyword.split())
            if word_count == 1:
                competition[keyword] = "High"
            elif word_count >= 4:
                competition[keyword] = "Low"
            else:
                competition[keyword] = "Medium"
        return competition