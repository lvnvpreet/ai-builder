import pytest
import numpy as np
from models.embeddings import EmbeddingModel

@pytest.fixture
def embedding_model():
    """Create and initialize an embedding model for testing."""
    model = EmbeddingModel("all-MiniLM-L6-v2")
    model.initialize()
    return model

def test_embedding_model_initialization(embedding_model):
    """Test that the embedding model initializes correctly."""
    assert embedding_model.model is not None
    assert embedding_model.model_name == "all-MiniLM-L6-v2"

def test_text_encoding(embedding_model):
    """Test that the model can encode text."""
    text = "This is a test sentence for embedding."
    embeddings = embedding_model.encode([text])
    
    # Check shape and type
    assert isinstance(embeddings, np.ndarray)
    assert len(embeddings.shape) == 2
    assert embeddings.shape[0] == 1
    
    # Sentence transformers typically output 384-dimensional embeddings for this model
    assert embeddings.shape[1] == 384

def test_template_embedding(embedding_model):
    """Test template embedding generation."""
    template_id = "test_template"
    template_data = {
        "name": "Test Template",
        "description": "A template for testing embedding generation.",
        "industries": ["testing", "technology"],
        "style": "modern",
        "features": ["test feature 1", "test feature 2"]
    }
    
    embedding = embedding_model.embed_template(template_id, template_data)
    
    # Check shape and type
    assert isinstance(embedding, np.ndarray)
    assert len(embedding.shape) == 1
    
    # Should be stored in cache
    assert template_id in embedding_model.embeddings_cache
    
    # Second call should use cached value
    cached_embedding = embedding_model.embed_template(template_id, template_data)
    assert np.array_equal(embedding, cached_embedding)

def test_embedding_cache_operations(embedding_model, tmp_path):
    """Test saving and loading of embedding cache."""
    # Add a test embedding to the cache
    template_id = "cache_test"
    template_data = {
        "name": "Cache Test",
        "description": "Testing cache operations",
        "industries": ["testing"],
        "features": ["test"]
    }
    
    # Generate embedding and add to cache
    embedding_model.embed_template(template_id, template_data)
    
    # Save cache to temporary file
    import os
    import joblib
    cache_file = tmp_path / "test_cache.pkl"
    joblib.dump(embedding_model.embeddings_cache, cache_file)
    
    # Create new model and load cache
    new_model = EmbeddingModel("all-MiniLM-L6-v2")
    new_model.embeddings_cache = joblib.load(cache_file)
    
    # Check that embedding is in the loaded cache
    assert template_id in new_model.embeddings_cache
    
    # Check that the embedding is the same
    original = embedding_model.embeddings_cache[template_id]
    loaded = new_model.embeddings_cache[template_id]
    assert np.array_equal(original, loaded)