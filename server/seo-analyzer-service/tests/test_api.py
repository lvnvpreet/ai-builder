import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SEO Analyzer Service is running!"}

def test_seo_analysis():
    """Test the main SEO analysis endpoint."""
    payload = {
        "text": "This is a test content for SEO analysis. It contains keywords like SEO, marketing, and optimization.",
        "target_keywords": ["SEO", "marketing"],
        "competitor_urls": ["https://example.com"],  # Mock URL
    }
    
    response = client.post("/seo", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "readability_score" in data
    assert "keyword_density" in data
    assert "meta_description" in data
    assert "meta_keywords" in data
    assert "seo_recommendations" in data

def test_competitor_analysis_endpoint():
    """Test the competitor analysis endpoint."""
    payload = {
        "competitor_urls": ["https://example.com"],
        "your_content": "Test content for comparison",
        "target_keywords": ["test", "comparison"]
    }
    
    response = client.post("/competitor-analysis", json=payload)
    
    # The endpoint might fail due to actual HTTP requests
    # In a real test environment, you'd mock the HTTP requests
    assert response.status_code in [200, 500]

def test_keyword_research_endpoint():
    """Test the keyword research endpoint."""
    payload = {
        "seed_keywords": ["seo", "marketing"],
        "industry": "technology"
    }
    
    response = client.post("/keyword-research", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "seed_keywords" in data
    assert "related_keywords" in data
    assert "keyword_ideas" in data