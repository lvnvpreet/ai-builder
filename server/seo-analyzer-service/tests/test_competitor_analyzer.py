import pytest
import asyncio
from analyzers.competitor_analyzer import CompetitorAnalyzer

@pytest.mark.asyncio
async def test_extract_seo_data():
    """Test SEO data extraction from HTML."""
    html = """
    <html>
        <head>
            <title>Test Website</title>
            <meta name="description" content="This is a test description">
            <meta name="keywords" content="test, website, seo">
        </head>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle</h2>
            <p>This is test content for SEO analysis.</p>
            <a href="/internal">Internal Link</a>
            <a href="https://external.com">External Link</a>
            <img src="test.jpg" alt="Test Image">
        </body>
    </html>
    """
    
    analyzer = CompetitorAnalyzer()
    data = analyzer.extract_seo_data(html, "https://test.com")
    
    assert data['title'] == "Test Website"
    assert data['meta_description'] == "This is a test description"
    assert data['meta_keywords'] == "test, website, seo"
    assert len(data['h1_tags']) == 1
    assert len(data['h2_tags']) == 1
    assert data['internal_links_count'] == 1
    assert data['external_links_count'] == 1
    assert data['images_count'] == 1
    assert data['images_with_alt'] == 1

@pytest.mark.asyncio
async def test_analyze_competitors():
    """Test competitor analysis with mock data."""
    analyzer = CompetitorAnalyzer()
    
    # Mock the fetch_url method to avoid actual HTTP requests
    async def mock_fetch_url(url):
        return """
        <html>
            <head><title>Competitor Site</title></head>
            <body>
                <h1>Competitor Content</h1>
                <p>This is competitor content for testing.</p>
            </body>
        </html>
        """
    
    analyzer.fetch_url = mock_fetch_url
    
    result = await analyzer.analyze_competitors(
        ["https://competitor1.com"],
        "Your content for testing",
        ["test", "seo"]
    )
    
    assert 'your_analysis' in result
    assert 'competitor_analysis' in result
    assert 'insights' in result
    assert len(result['competitor_analysis']) == 1