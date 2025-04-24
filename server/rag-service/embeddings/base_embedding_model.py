"""
Base class for embedding models in the RAG service.
All embedding model implementations should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional
import logging
import numpy as np

class BaseEmbeddingModel(ABC):
    """Base class for embedding models."""
    
    def __init__(self, model_name: str):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name or path of the model to load
        """
        self.model_name = model_name
        self.model = None
        self.dimension = None
        self.logger = logging.getLogger(f"rag_service.embeddings.{self.__class__.__name__}")
    
    @abstractmethod
    def load(self) -> bool:
        """
        Load the embedding model.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Dimension of the embedding vectors
        """
        pass
    
    def encode_queries(self, queries: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode queries (default same as encode, override if query encoding differs).
        
        Args:
            queries: Single query or list of queries to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of query embeddings
        """
        # By default, query encoding is the same as document encoding
        return self.encode(queries, batch_size)
    
    def encode_documents(self, documents: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode documents (default same as encode, override if document encoding differs).
        
        Args:
            documents: Single document or list of documents to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of document embeddings
        """
        # By default, document encoding is the same as query encoding
        return self.encode(documents, batch_size)
    
    def similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate similarity between query and document embeddings.
        
        Args:
            query_embedding: Query embedding
            doc_embeddings: Document embeddings
            
        Returns:
            Array of similarity scores
        """
        # Default implementation uses cosine similarity
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Normalize embeddings for cosine similarity
        query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        doc_norm = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        
        normalized_query = query_embedding / (query_norm + 1e-8)
        normalized_docs = doc_embeddings / (doc_norm + 1e-8)
        
        # Calculate cosine similarity (dot product of normalized vectors)
        return np.dot(normalized_query, normalized_docs.T)[0]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "dimension": self.get_dimension(),
            "type": self.__class__.__name__
        }