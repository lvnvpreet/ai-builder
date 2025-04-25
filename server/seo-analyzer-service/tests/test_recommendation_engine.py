import pytest
from analyzers.recommendation_engine import SEORecommendationEngine

def test_generate_readability_recommendations():
    """Test readability recommendations."""
    engine = SEORecommendationEngine()
    
    # Test with low readability score
    recommendations = engine.generate_readability_recommendations(25.0)
    
    assert len(recommendations) > 0
    assert recommendations[0]['priority'] == 'critical'
    assert 'readability' in recommendations[0]['type']
    
    # Test with good readability score
    recommendations = engine.generate_readability_recommendations(70.0)
    
    assert len(recommendations) == 0

def test_generate_keyword_recommendations():
    """Test keyword density recommendations."""
    engine = SEORecommendationEngine()
    
    keyword_density = {
        "seo": 0.0005,  # Too low
        "marketing": 0.04,  # Too high
        "digital": 0.015  # Just right
    }
    
    recommendations = engine.generate_keyword_recommendations(keyword_density)
    
    assert len(recommendations) == 2  # One for "seo", one for "marketing"
    assert any("seo" in rec['issue'] for rec in recommendations)
    assert any("marketing" in rec['issue'] for rec in recommendations)

def test_full_recommendation_generation():
    """Test complete recommendation generation."""
    engine = SEORecommendationEngine()
    
    recommendations = engine.generate_recommendations(
        readability_score=45.0,
        keyword_density={"seo": 0.001},
        competitor_analysis={
            "insights": {
                "weaknesses": ["Content is shorter than competitors"]
            }
        },
        keyword_opportunities={
            "long_tail_opportunities": ["best seo tools 2024"]
        },
        content_gaps={
            "topic_gaps": [{"topic": "advanced seo", "importance": "high"}]
        }
    )
    
    assert len(recommendations) > 0
    assert any(rec['priority'] == 'critical' for rec in recommendations)