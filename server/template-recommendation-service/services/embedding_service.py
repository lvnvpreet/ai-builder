import logging
from typing import List, Dict, Any
import numpy as np
from models.embeddings import EmbeddingModel

logger = logging.getLogger("template_recommender.embedding_service")

class EmbeddingService:
    """Service for generating and managing text embeddings."""
    
    def __init__(self, model_name: str = None):
        """Initialize with the specified model or default."""
        self.embedding_model = EmbeddingModel(model_name)
        
    def initialize(self):
        """Initialize the embedding model."""
        self.embedding_model.initialize()
        
    def get_query_embedding(self, 
                          business_name: str,
                          business_description: str,
                          industry: str,
                          target_audience: List[str] = None,
                          unique_selling_points: List[str] = None) -> np.ndarray:
        """
        Generate a rich query embedding from business information.
        
        Args:
            business_name: Name of the business
            business_description: Description of the business
            industry: Business industry
            target_audience: Target audience descriptors
            unique_selling_points: Unique selling points
            
        Returns:
            Embedding vector for the query
        """
        # Combine all business information into a rich query text
        query_text = f"{business_name}. {business_description}. "
        if target_audience:
            query_text += f"Target audience: {', '.join(target_audience)}. "
        if unique_selling_points:
            query_text += f"Unique selling points: {', '.join(unique_selling_points)}. "
        query_text += f"Industry: {industry}."
        
        logger.debug(f"Generated query text: {query_text[:100]}...")
        
        # Get query embedding
        return self.embedding_model.encode([query_text])[0]
        
    def get_template_embeddings(self, templates: Dict[str, Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        Get embeddings for all templates.
        
        Args:
            templates: Dict mapping template IDs to their metadata
            
        Returns:
            Dict mapping template IDs to their embeddings
        """
        embeddings = {}
        
        for template_id, template_data in templates.items():
            embeddings[template_id] = self.embedding_model.embed_template(template_id, template_data)
            
        return embeddings
        
    def save_embeddings(self):
        """Save template embeddings to disk."""
        self.embedding_model.save_embeddings_cache()