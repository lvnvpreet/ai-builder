"""
Cohere embedding model implementation.
Provides embeddings using Cohere's embedding API.
"""

import os
from typing import List, Union, Optional, Dict, Any
import numpy as np
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_embedding_model import BaseEmbeddingModel

class CohereEmbedding(BaseEmbeddingModel):
    """Cohere embedding model."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize Cohere embedding model.
        
        Args:
            model_name: Name of the Cohere embedding model to use
        """
        # Use default model if not specified
        if model_name is None or not model_name:
            model_name = os.getenv("COHERE_EMBEDDING_MODEL", "embed-english-v3.0")
            
        # If only model type is specified without specific model, use a default
        if model_name == "cohere":
            model_name = "embed-english-v3.0"
            
        # Remove prefix if present
        if model_name.startswith("cohere/"):
            model_name = model_name[len("cohere/"):]
            
        super().__init__(model_name)
        
        # Get API key from environment
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            self.logger.warning("Cohere API key not found in environment variables")
            
        # Embedding dimensions for Cohere models
        self.dimensions_map = {
            "embed-english-v3.0": 1024,
            "embed-english-light-v3.0": 384,
            "embed-multilingual-v3.0": 1024,
            "embed-multilingual-light-v3.0": 384
        }
        
        self.api_base_url = "https://api.cohere.ai/v1/embed"
        self.client = None
        self.load()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def load(self) -> bool:
        """
        Initialize the httpx client for Cohere API.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.api_key:
                self.logger.error("Cohere API key is required")
                return False
                
            self.logger.info(f"Initializing Cohere embedding model: {self.model_name}")
            self.client = httpx.AsyncClient(timeout=60.0)
            
            # Get dimension from map or use default
            self.dimension = self.dimensions_map.get(self.model_name, 1024)
            
            self.logger.info(f"Successfully initialized Cohere embedding with dimension: {self.dimension}")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Cohere client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    async def encode_async(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings using Cohere API asynchronously.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if self.client is None:
            self.load()
            
        if isinstance(texts, str):
            texts = [texts]
            
        # Log input for debugging (truncate for privacy)
        if len(texts) == 1:
            self.logger.debug(f"Encoding text: {texts[0][:100]}{'...' if len(texts[0]) > 100 else ''}")
        else:
            self.logger.debug(f"Encoding {len(texts)} texts with batch size {batch_size}")
            
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "texts": batch,
                    "model": self.model_name,
                    "truncate": "END"  # Truncate from the end if text is too long
                }
                
                response = await self.client.post(
                    self.api_base_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # Extract embeddings from response
                batch_embeddings = response_data.get("embeddings", [])
                all_embeddings.extend(batch_embeddings)
                
            except httpx.HTTPError as e:
                self.logger.error(f"Cohere API HTTP error during encoding: {str(e)}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error during encoding: {str(e)}")
                raise
        
        return np.array(all_embeddings)
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings using Cohere API (synchronous wrapper).
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        # Since Cohere client is async, we need to run it in an event loop
        import asyncio
        
        # Get the current event loop or create a new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the async function to completion
        return loop.run_until_complete(self.encode_async(texts, batch_size))
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Dimension of the embedding vectors
        """
        return self.dimension or self.dimensions_map.get(self.model_name, 1024)
    
    def encode_queries(self, queries: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode queries optimized for search.
        
        Args:
            queries: Single query or list of queries to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of query embeddings
        """
        # For Cohere, we could use a specific input_type parameter for queries
        # This would be implemented in the async function
        return self.encode(queries, batch_size)
    
    def encode_documents(self, documents: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode documents optimized for storage.
        
        Args:
            documents: Single document or list of documents to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of document embeddings
        """
        # For Cohere, we could use a specific input_type parameter for documents
        # This would be implemented in the async function
        return self.encode(documents, batch_size)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        
        # Add Cohere specific info
        info.update({
            "api_provider": "Cohere",
            "supports_multilingual": "multilingual" in self.model_name,
            "api_version": "v1"
        })
            
        return info