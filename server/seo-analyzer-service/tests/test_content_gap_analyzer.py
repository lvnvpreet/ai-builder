import pytest
from analyzers.content_gap_analyzer import ContentGapAnalyzer
import spacy

@pytest.fixture
def content_gap_analyzer():
    nlp = spacy.load("en_core_web_sm")
    return ContentGapAnalyzer(nlp)

def test_analyze_content_structure(content_gap_analyzer):
    """Test content structure analysis."""
    content = """
    # Main Title
    
    This is a paragraph.
    
    ## Subtitle
    
    Another paragraph here.
    
    - List item 1
    - List item 2
    """
    
    structure = content_gap_analyzer.analyze_content_structure(content)
    
    assert structure['paragraph_count'] > 0
    assert structure['word_count'] > 0
    assert structure['header_count'] > 0

@pytest.mark.asyncio
async def test_find_gaps(content_gap_analyzer):
    """Test content gap analysis with mock data."""
    # Mock the fetch_competitor_content method
    async def mock_fetch_content(url):
        return "Competitor content about SEO and digital marketing strategies."
    
    content_gap_analyzer.fetch_competitor_content = mock_fetch_content
    
    your_content = "Basic SEO content without much detail."
    competitor_urls = ["https://competitor.com"]
    
    gaps = await content_gap_analyzer.find_gaps(your_content, competitor_urls, ["SEO"])
    
    assert 'topic_gaps' in gaps
    assert 'depth_gaps' in gaps
    assert 'keyword_gaps' in gaps
    assert 'semantic_gaps' in gaps
    assert 'recommendations' in gaps