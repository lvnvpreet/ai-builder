"""
Sentence Transformers embedding model implementation.
Provides embeddings using HuggingFace's sentence-transformers models.
"""

import os
from typing import List, Union, Optional, Dict, Any
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sentence_transformers import SentenceTransformer

from .base_embedding_model import BaseEmbeddingModel

class SentenceTransformerEmbedding(BaseEmbeddingModel):
    """Sentence Transformers embedding model."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize Sentence Transformers model.
        
        Args:
            model_name: Name or path of the model to load
        """
        # Use default model if not specified
        if model_name is None or not model_name:
            model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
            
        # If only model type is specified without specific model, use a default
        if model_name == "sentence-transformers":
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
        # Remove prefix if present
        if model_name.startswith("sentence-transformers/"):
            model_name = model_name[len("sentence-transformers/"):]
            
        super().__init__(model_name)
        self.load()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def load(self) -> bool:
        """
        Load the Sentence Transformers model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading Sentence Transformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Successfully loaded model with dimension: {self.dimension}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading Sentence Transformers model: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((RuntimeError, OSError))
    )
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self.load()
            
        if isinstance(texts, str):
            texts = [texts]
            
        # Log input for debugging (truncate for privacy)
        if len(texts) == 1:
            self.logger.debug(f"Encoding text: {texts[0][:100]}{'...' if len(texts[0]) > 100 else ''}")
        else:
            self.logger.debug(f"Encoding {len(texts)} texts with batch size {batch_size}")
            
        try:
            # Use the Sentence Transformers encode method
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            
            return embeddings
        except (RuntimeError, OSError) as e:
            self.logger.error(f"Error during encoding: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during encoding: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Dimension of the embedding vectors
        """
        if self.dimension is None and self.model is not None:
            self.dimension = self.model.get_sentence_embedding_dimension()
        return self.dimension or 0
    
    def encode_queries(self, queries: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode queries (optimized for query encoding).
        
        Args:
            queries: Single query or list of queries to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of query embeddings
        """
        # For some models, query encoding might be different from document encoding
        # For sentence-transformers, we'll keep it the same for now
        return self.encode(queries, batch_size)
    
    def encode_documents(self, documents: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode documents (optimized for document encoding).
        
        Args:
            documents: Single document or list of documents to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of document embeddings
        """
        # For some models, document encoding might be different from query encoding
        # For sentence-transformers, we'll keep it the same for now
        return self.encode(documents, batch_size)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        
        # Add Sentence Transformers specific info if model is loaded
        if self.model is not None:
            info.update({
                "max_seq_length": self.model.max_seq_length,
                "model_path": str(self.model.model_path),
                "pooling_strategy": str(self.model._modules.get('1', 'unknown'))
            })
            
        return info