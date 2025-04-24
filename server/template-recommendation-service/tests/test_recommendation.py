import pytest
import numpy as np
from models.recommendation import RecommendationModel

@pytest.fixture
def recommendation_model():
    """Create a recommendation model for testing."""
    return RecommendationModel()

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    # Sample query embedding
    query_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    
    # Sample template embeddings
    template_embeddings = {
        "template1": np.array([0.1, 0.2, 0.3, 0.4, 0.5]),  # Perfect match
        "template2": np.array([0.5, 0.4, 0.3, 0.2, 0.1]),  # Different
        "template3": np.array([0.15, 0.25, 0.35, 0.45, 0.55]),  # Similar
        "template4": np.array([0.0, 0.0, 0.0, 0.0, 0.0]),  # Zero vector
    }
    
    # Sample template data
    template_data = {
        "template1": {
            "name": "Perfect Match",
            "industries": ["technology"],
            "features": ["feature1", "feature2"],
        },
        "template2": {
            "name": "Different Template",
            "industries": ["retail"],
            "features": ["feature3", "feature4"],
        },
        "template3": {
            "name": "Similar Template",
            "industries": ["technology", "software"],
            "features": ["feature1", "feature5"],
        },
        "template4": {
            "name": "Empty Template",
            "industries": [],
            "features": [],
        }
    }
    
    return {
        "query_embedding": query_embedding,
        "template_embeddings": template_embeddings,
        "template_data": template_data
    }

def test_rank_templates_basic(recommendation_model, sample_data):
    """Test basic template ranking."""
    rankings = recommendation_model.rank_templates(
        query_embedding=sample_data["query_embedding"],
        template_embeddings=sample_data["template_embeddings"],
        template_data=sample_data["template_data"],
        top_k=4
    )
    
    # Should return 4 templates
    assert len(rankings) == 4
    
    # First one should be the perfect match
    assert rankings[0]["templateId"] == "template1"
    
    # Check that scores are in descending order
    scores = [r["score"] for r in rankings]
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

def test_rank_templates_with_industry(recommendation_model, sample_data):
    """Test template ranking with industry boost."""
    # Rank with technology industry
    rankings_tech = recommendation_model.rank_templates(
        query_embedding=sample_data["query_embedding"],
        template_embeddings=sample_data["template_embeddings"],
        template_data=sample_data["template_data"],
        industry="technology",
        top_k=4
    )
    
    # Rank with retail industry
    rankings_retail = recommendation_model.rank_templates(
        query_embedding=sample_data["query_embedding"],
        template_embeddings=sample_data["template_embeddings"],
        template_data=sample_data["template_data"],
        industry="retail",
        top_k=4
    )
    
    # Template1 and Template3 should get industry boost for technology
    tech_scores = {r["templateId"]: r["score"] for r in rankings_tech}
    retail_scores = {r["templateId"]: r["score"] for r in rankings_retail}
    
    # Check that Template1 gets higher score with technology industry
    assert tech_scores["template1"] > retail_scores["template1"]
    
    # Check that Template2 gets higher score with retail industry
    assert retail_scores["template2"] > tech_scores["template2"]

def test_industry_boost_calculation(recommendation_model):
    """Test industry boost calculation."""
    # Test exact match
    boost = recommendation_model._calculate_industry_boost(
        industry="technology",
        template_metadata={"industries": ["technology", "software"]}
    )
    assert boost == 0.2
    
    # Test partial match
    boost = recommendation_model._calculate_industry_boost(
        industry="tech",
        template_metadata={"industries": ["technology", "software"]}
    )
    assert boost == 0.1
    
    # Test no match
    boost = recommendation_model._calculate_industry_boost(
        industry="retail",
        template_metadata={"industries": ["technology", "software"]}
    )
    assert boost == 0.0
    
    # Test empty industry
    boost = recommendation_model._calculate_industry_boost(
        industry="",
        template_metadata={"industries": ["technology", "software"]}
    )
    assert boost == 0.0
    
    # Test missing industries in metadata
    boost = recommendation_model._calculate_industry_boost(
        industry="technology",
        template_metadata={}
    )
    assert boost == 0.0

def test_feature_boost_calculation(recommendation_model):
    """Test feature boost calculation."""
    # Test many features
    boost = recommendation_model._calculate_feature_boost(
        template_metadata={"features": ["f1", "f2", "f3", "f4", "f5"]}
    )
    assert boost == 0.1
    
    # Test few features
    boost = recommendation_model._calculate_feature_boost(
        template_metadata={"features": ["f1", "f2", "f3"]}
    )
    assert boost == 0.05
    
    # Test very few features
    boost = recommendation_model._calculate_feature_boost(
        template_metadata={"features": ["f1", "f2"]}
    )
    assert boost == 0.0
    
    # Test missing features
    boost = recommendation_model._calculate_feature_boost(
        template_metadata={}
    )
    assert boost == 0.0