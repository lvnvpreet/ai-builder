from sentence_transformers import SentenceTransformer
import numpy as np
import os
import logging
from typing import List, Dict, Any
import joblib
import config

logger = logging.getLogger("template_recommender.embeddings")

class EmbeddingModel:
    """Text embedding model using sentence transformers."""
    
    def __init__(self, model_name: str = None):
        """Initialize with specified model or use default from config."""
        self.model_name = model_name or config.MODEL_NAME
        self.model = None
        self.embeddings_cache = {}
        
    def initialize(self):
        """Load the model and cached embeddings."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully")
            
            # Load cached embeddings if available
            if os.path.exists(config.TEMPLATE_EMBEDDINGS_PATH):
                logger.info("Loading cached template embeddings")
                self.embeddings_cache = joblib.load(config.TEMPLATE_EMBEDDINGS_PATH)
                logger.info(f"Loaded {len(self.embeddings_cache)} cached embeddings")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        if self.model is None:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        return self.model.encode(texts, show_progress_bar=False)
    
    def embed_template(self, template_id: str, template_data: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for a template based on its description and features."""
        if template_id in self.embeddings_cache:
            return self.embeddings_cache[template_id]
            
        # Combine template description, industry, and features into a rich text representation
        template_text = f"{template_data['name']}. {template_data['description']}. "
        template_text += f"Industries: {', '.join(template_data.get('industries', []))}. "
        template_text += f"Features: {', '.join(template_data.get('features', []))}. "
        template_text += f"Style: {template_data.get('style', '')}. "
        
        embedding = self.encode([template_text])[0]
        self.embeddings_cache[template_id] = embedding
        return embedding
        
    def save_embeddings_cache(self):
        """Save the embeddings cache to disk."""
        os.makedirs(os.path.dirname(config.TEMPLATE_EMBEDDINGS_PATH), exist_ok=True)
        joblib.dump(self.embeddings_cache, config.TEMPLATE_EMBEDDINGS_PATH)
        logger.info(f"Saved {len(self.embeddings_cache)} embeddings to cache")