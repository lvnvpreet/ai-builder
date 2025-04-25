import pytest
from analyzers.keyword_analyzer import KeywordAnalyzer
import spacy

@pytest.fixture
def keyword_analyzer():
    nlp = spacy.load("en_core_web_sm")
    return KeywordAnalyzer(nlp)

def test_find_semantic_variations(keyword_analyzer):
    """Test finding semantic variations of keywords."""
    target_keywords = ["marketing"]
    existing_keywords = {"digital marketing": 0.1, "marketing strategy": 0.2}
    
    variations = keyword_analyzer.find_semantic_variations(target_keywords, existing_keywords)
    
    assert "marketing" in variations
    assert len(variations["marketing"]) > 0

def test_generate_variations(keyword_analyzer):
    """Test keyword variation generation."""
    variations = keyword_analyzer.generate_variations("service")
    
    assert "services" in variations
    assert any("best service" in v for v in variations)
    assert any("service solutions" in v for v in variations)

def test_find_long_tail_keywords(keyword_analyzer):
    """Test long-tail keyword identification."""
    text = "digital marketing strategy for small businesses in 2024"
    doc = keyword_analyzer.nlp(text)
    
    long_tail = keyword_analyzer.find_long_tail_keywords(doc, ["marketing"])
    
    assert len(long_tail) > 0
    assert any("marketing" in kw for kw in long_tail)

def test_find_question_keywords(keyword_analyzer):
    """Test question keyword extraction."""
    text = "What is SEO? How to improve website ranking? When should you start SEO?"
    doc = keyword_analyzer.nlp(text)
    
    questions = keyword_analyzer.find_question_keywords(doc)
    
    assert len(questions) == 3
    assert "What is SEO?" in questions