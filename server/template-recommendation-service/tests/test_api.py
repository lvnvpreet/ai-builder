import pytest
from fastapi.testclient import TestClient
import os
import json
import sys
import uuid

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_recommendation_input():
    """Create a sample recommendation input for testing."""
    return {
        "sessionId": str(uuid.uuid4()),
        "processed_input": {
            "business_name": "TechSolutions",
            "industry": "technology",
            "description": "We provide innovative software solutions for businesses.",
            "target_audience": ["small businesses", "startups"],
            "unique_selling_points": ["24/7 support", "custom development"]
        }
    }

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Template Recommendation Service is running!"}

def test_recommend_templates(client, sample_recommendation_input):
    """Test the recommend-templates endpoint."""
    response = client.post("/recommend-templates", json=sample_recommendation_input)
    
    # Check response status
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "sessionId" in data
    assert "recommendations" in data
    assert data["sessionId"] == sample_recommendation_input["sessionId"]
    
    # Check recommendations
    recommendations = data["recommendations"]
    assert isinstance(recommendations, list)
    
    if recommendations:  # If any recommendations returned
        # Check first recommendation structure
        first_rec = recommendations[0]
        assert "templateId" in first_rec
        assert "score" in first_rec
        assert "matchReason" in first_rec
        
        # Score should be between 0 and 1
        assert 0 <= first_rec["score"] <= 1

def test_recommend_templates_missing_fields(client):
    """Test the recommend-templates endpoint with missing fields."""
    # Missing sessionId
    response = client.post("/recommend-templates", json={
        "processed_input": {
            "business_name": "Test",
            "industry": "test"
        }
    })
    assert response.status_code == 422  # Validation error
    
    # Missing processed_input
    response = client.post("/recommend-templates", json={
        "sessionId": str(uuid.uuid4())
    })
    assert response.status_code == 422  # Validation error

def test_recommend_templates_empty_description(client, sample_recommendation_input):
    """Test the recommend-templates endpoint with an empty business description."""
    # Copy the input and remove the description
    modified_input = sample_recommendation_input.copy()
    modified_input["processed_input"] = modified_input["processed_input"].copy()
    modified_input["processed_input"]["description"] = ""
    
    response = client.post("/recommend-templates", json=modified_input)
    
    # Should still work
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)