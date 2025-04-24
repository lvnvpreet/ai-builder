import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger("template_recommender.recommendation")

class RecommendationModel:
    """Model for recommending templates based on semantic similarity."""
    
    def __init__(self):
        """Initialize the recommendation model."""
        pass
        
    def rank_templates(self, 
                      query_embedding: np.ndarray, 
                      template_embeddings: Dict[str, np.ndarray],
                      template_data: Dict[str, Dict[str, Any]],
                      industry: str = "",
                      top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rank templates based on semantic similarity to the query.
        
        Args:
            query_embedding: Embedding vector of the user query/business description
            template_embeddings: Dict mapping template IDs to their embeddings
            template_data: Dict mapping template IDs to their metadata
            industry: Business industry for industry-specific boosting
            top_k: Number of top templates to return
            
        Returns:
            List of dicts with template IDs, scores and metadata
        """
        # Calculate scores for all templates
        template_scores = []
        
        for template_id, embedding in template_embeddings.items():
            template_metadata = template_data.get(template_id, {})
            
            # Calculate cosine similarity
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            
            # Calculate additional boosts
            industry_boost = self._calculate_industry_boost(industry, template_metadata)
            feature_boost = self._calculate_feature_boost(template_metadata)
            
            # Final score is similarity plus any boosts, capped at 1.0
            final_score = min(similarity + industry_boost + feature_boost, 1.0)
            
            template_scores.append({
                'templateId': template_id,
                'score': final_score,
                'similarity': similarity,
                'industry_boost': industry_boost,
                'feature_boost': feature_boost,
                'templateData': template_metadata
            })
        
        # Sort by score (descending) and take top_k
        template_scores.sort(key=lambda x: x['score'], reverse=True)
        return template_scores[:top_k]
        
    def _calculate_industry_boost(self, industry: str, template_metadata: Dict[str, Any]) -> float:
        """
        Calculate boost based on industry match.
        
        Args:
            industry: Business industry
            template_metadata: Template metadata with industries list
            
        Returns:
            Boost value (0.0-0.2)
        """
        if not industry or 'industries' not in template_metadata:
            return 0.0
            
        # Direct match
        if any(i.lower() == industry.lower() for i in template_metadata.get('industries', [])):
            return 0.2
            
        # Partial match (e.g., "tech" in "technology")
        if any(i.lower() in industry.lower() or industry.lower() in i.lower() 
               for i in template_metadata.get('industries', [])):
            return 0.1
        
        return 0.0
        
    def _calculate_feature_boost(self, template_metadata: Dict[str, Any]) -> float:
        """
        Calculate boost based on template features.
        
        Args:
            template_metadata: Template metadata
            
        Returns:
            Boost value (0.0-0.1)
        """
        # Award a small boost for templates with more features
        features = template_metadata.get('features', [])
        if len(features) >= 5:
            return 0.1
        elif len(features) >= 3:
            return 0.05
        
        return 0.0