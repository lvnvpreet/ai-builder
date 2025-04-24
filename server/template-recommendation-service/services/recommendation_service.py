import os
import json
import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from models.embeddings import EmbeddingModel
from models.recommendation import RecommendationModel
from models.schema import TemplateRecommendation
from services.embedding_service import EmbeddingService
from services.template_service import TemplateService
from utils.explanation import generate_match_reason

logger = logging.getLogger("template_recommender.recommendation_service")

class RecommendationService:
    """Service for generating template recommendations."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.template_service = TemplateService()
        self.embedding_service = EmbeddingService()
        self.recommendation_model = RecommendationModel()
        
    def initialize(self):
        """Initialize models and load template data."""
        try:
            # Initialize template service (load templates data)
            self.template_service.initialize()
            
            # Initialize embedding service
            self.embedding_service.initialize()
            
            # Pre-compute embeddings for all templates
            templates = self.template_service.get_all_templates()
            self.embedding_service.get_template_embeddings(templates)
            
            # Save the updated embeddings cache
            self.embedding_service.save_embeddings()
            
        except Exception as e:
            logger.error(f"Error initializing recommendation service: {str(e)}")
            raise
    
    def get_recommendations(self, 
                           business_description: str,
                           industry: str,
                           business_name: str, 
                           target_audience: List[str] = None,
                           unique_selling_points: List[str] = None,
                           top_k: int = 5) -> List[TemplateRecommendation]:
        """
        Get template recommendations based on business information.
        
        Args:
            business_description: Description of the business
            industry: Business industry
            business_name: Name of the business
            target_audience: List of target audience descriptors
            unique_selling_points: List of unique selling points
            top_k: Number of recommendations to return
            
        Returns:
            List of template recommendations
        """
        if not business_description:
            business_description = f"{business_name} in the {industry} industry"
            
        if not business_name:
            business_name = "Business"
            
        if not target_audience:
            target_audience = []
            
        if not unique_selling_points:
            unique_selling_points = []
            
        # Get all templates
        templates = self.template_service.get_all_templates()
        
        # Generate query embedding
        query_embedding = self.embedding_service.get_query_embedding(
            business_name=business_name,
            business_description=business_description,
            industry=industry,
            target_audience=target_audience,
            unique_selling_points=unique_selling_points
        )
        
        # Get template embeddings
        template_embeddings = self.embedding_service.get_template_embeddings(templates)
        
        # Rank templates
        ranked_templates = self.recommendation_model.rank_templates(
            query_embedding=query_embedding,
            template_embeddings=template_embeddings,
            template_data=templates,
            industry=industry,
            top_k=top_k
        )
        
        # Format as TemplateRecommendation objects
        recommendations = []
        for template in ranked_templates:
            template_data = template['templateData']
            match_reason = generate_match_reason(
                template_data=template_data, 
                industry=industry,
                score=template['score'],
                target_audience=target_audience
            )
            
            recommendations.append(
                TemplateRecommendation(
                    templateId=template['templateId'],
                    score=round(template['score'], 2),
                    matchReason=match_reason,
                    previewUrl=template_data.get('previewUrl'),
                    features=template_data.get('features', [])
                )
            )
        
        return recommendations