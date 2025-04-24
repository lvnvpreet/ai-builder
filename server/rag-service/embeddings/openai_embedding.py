"""
OpenAI embedding model implementation.
Provides embeddings using OpenAI's embedding API.
"""

import os
from typing import List, Union, Optional, Dict, Any
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI, OpenAIError
import tiktoken

from .base_embedding_model import BaseEmbeddingModel

class OpenAIEmbedding(BaseEmbeddingModel):
    """OpenAI embedding model."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize OpenAI embedding model.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
        """
        # Use default model if not specified
        if model_name is None or not model_name:
            model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            
        # If only model type is specified without specific model, use a default
        if model_name == "openai":
            model_name = "text-embedding-3-small"
            
        # Remove prefix if present
        if model_name.startswith("openai/"):
            model_name = model_name[len("openai/"):]
            
        super().__init__(model_name)
        
        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.logger.warning("OpenAI API key not found in environment variables")
            
        # Embedding dimensions for OpenAI models
        self.dimensions_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        self.client = None
        self.tiktoken_encoder = None
        self.load()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def load(self) -> bool:
        """
        Initialize the OpenAI client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.api_key:
                self.logger.error("OpenAI API key is required")
                return False
                
            self.logger.info(f"Initializing OpenAI embedding model: {self.model_name}")
            self.client = OpenAI(api_key=self.api_key)
            
            # Get dimension from map or use default
            self.dimension = self.dimensions_map.get(self.model_name, 1536)
            
            # Load tiktoken for token counting
            try:
                self.tiktoken_encoder = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
                
            self.logger.info(f"Successfully initialized OpenAI embedding with dimension: {self.dimension}")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(OpenAIError)
    )
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) to embeddings using OpenAI API.
        
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
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch,
                    encoding_format="float"
                )
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
            except OpenAIError as e:
                self.logger.error(f"OpenAI API error during encoding: {str(e)}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error during encoding: {str(e)}")
                raise
        
        return np.array(all_embeddings)
    
    def get_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Dimension of the embedding vectors
        """
        return self.dimension or self.dimensions_map.get(self.model_name, 1536)
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.tiktoken_encoder is None:
            try:
                self.tiktoken_encoder = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
                
        return len(self.tiktoken_encoder.encode(text))
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        
        # Add OpenAI specific info
        info.update({
            "api_provider": "OpenAI",
            "token_counter": "tiktoken",
            "max_token_limit": 8191 if self.model_name == "text-embedding-3-large" else 4096
        })
            
        return info