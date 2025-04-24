"""
Ollama embedding model implementation.
Provides embeddings using locally-hosted Ollama models.
"""

import os
import json
from typing import List, Union, Optional, Dict, Any
import numpy as np
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_embedding_model import BaseEmbeddingModel

class OllamaEmbedding(BaseEmbeddingModel):
    """Ollama embedding model for local open-source models."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize Ollama embedding model.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        # Use default model if not specified
        if model_name is None or not model_name:
            model_name = os.getenv("OLLAMA_EMBEDDING_MODEL", "llama3")
            
        # If only model type is specified without specific model, use a default
        if model_name == "ollama":
            model_name = "llama3"
            
        # Remove prefix if present
        if model_name.startswith("ollama/"):
            model_name = model_name[len("ollama/"):]
            
        super().__init__(model_name)
        
        # Get Ollama API base URL from environment or use default
        self.api_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Embedding dimensions for common Ollama models (approximate values)
        self.dimensions_map = {
            "llama3": 4096,
            "llama2": 4096,
            "mistral": 4096,
            "mixtral": 4096,
            "phi3": 2048,
            "gemma": 2048,
            "orca-mini": 3072
        }
        
        self.client = None
        self.load()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def load(self) -> bool:
        """
        Initialize the httpx client for Ollama API.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing Ollama embedding model: {self.model_name}")
            self.client = httpx.Client(timeout=60.0)
            
            # Check if the model is available by making a ping request
            ping_url = f"{self.api_base_url}/api/tags"
            response = self.client.get(ping_url)
            response.raise_for_status()
            
            # Get dimension from map or use default
            base_model = self.model_name.split(':')[0] if ':' in self.model_name else self.model_name
            self.dimension = self.dimensions_map.get(base_model, 4096)
            
            self.logger.info(f"Successfully initialized Ollama embedding with dimension: {self.dimension}")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Ollama client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    def encode(self, texts: Union[str, List[str]], batch_size: int = 8) -> np.ndarray:
        """
        Encode text(s) to embeddings using Ollama API.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding (smaller than other providers due to local resource constraints)
            
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
        embed_url = f"{self.api_base_url}/api/embeddings"
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = []
            
            for text in batch:
                try:
                    payload = {
                        "model": self.model_name,
                        "prompt": text
                    }
                    
                    response = self.client.post(
                        embed_url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Extract embedding from response
                    embedding = response_data.get("embedding", [])
                    if embedding:
                        batch_embeddings.append(embedding)
                    else:
                        self.logger.warning(f"No embedding returned for text: {text[:30]}...")
                        # Use a zero vector as a fallback
                        batch_embeddings.append(np.zeros(self.dimension).tolist())
                        
                except httpx.HTTPError as e:
                    self.logger.error(f"Ollama API HTTP error during encoding: {str(e)}")
                    raise
                except Exception as e:
                    self.logger.error(f"Unexpected error during encoding: {str(e)}")
                    raise
            
            all_embeddings.extend(batch_embeddings)
        
        return np.array(all_embeddings)
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Dimension of the embedding vectors
        """
        return self.dimension or 4096  # Default dimension for most Ollama models
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        
        # Add Ollama specific info
        info.update({
            "api_provider": "Ollama",
            "api_url": self.api_base_url,
            "open_source": True,
            "local_deployment": True
        })
            
        return info