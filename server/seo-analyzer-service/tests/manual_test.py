import requests
import json

def test_seo_service():
    """Manual testing script for SEO Analyzer Service."""
    
    base_url = "http://localhost:3006"
    
    # Test 1: Basic SEO Analysis
    print("\n=== Test 1: Basic SEO Analysis ===")
    
    content = """
    Understanding SEO: A Comprehensive Guide
    
    Search Engine Optimization (SEO) is the practice of improving your website to increase 
    its visibility in search engine results. In today's digital landscape, SEO is crucial 
    for businesses of all sizes.
    
    Key Components of SEO:
    1. On-page optimization
    2. Technical SEO
    3. Content creation
    4. Link building
    
    This guide will help you understand the fundamentals of SEO and how to implement 
    effective strategies for your website.
    """
    
    payload = {
        "text": content,
        "target_keywords": ["SEO", "optimization", "search engine"],
        "competitor_urls": [
            "https://moz.com/beginners-guide-to-seo",
            "https://searchengineland.com/guide/what-is-seo"
        ]
    }
    
    response = requests.post(f"{base_url}/seo", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Readability Score: {result.get('readability_score')}")
        print(f"Keyword Density: {result.get('keyword_density')}")
        print(f"SEO Recommendations: {len(result.get('seo_recommendations', []))} found")
        
        if result.get('seo_recommendations'):
            print("\nTop 3 Recommendations:")
            for rec in result['seo_recommendations'][:3]:
                print(f"- [{rec['priority']}] {rec['recommendation']}")
    
    # Test 2: Competitor Analysis
    print("\n=== Test 2: Competitor Analysis ===")
    
    comp_payload = {
        "competitor_urls": ["https://example.com"],
        "your_content": content,
        "target_keywords": ["SEO", "optimization"]
    }
    
    response = requests.post(f"{base_url}/competitor-analysis", json=comp_payload)
    print(f"Status: {response.status_code}")
    
    # Test 3: Keyword Research
    print("\n=== Test 3: Keyword Research ===")
    
    keyword_payload = {
        "seed_keywords": ["SEO", "digital marketing", "website optimization"],
        "industry": "technology"
    }
    
    response = requests.post(f"{base_url}/keyword-research", json=keyword_payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result.get('keyword_ideas', []))} keyword ideas")
        
        if result.get('keyword_ideas'):
            print("\nTop 5 Keyword Ideas:")
            for idea in result['keyword_ideas'][:5]:
                print(f"- {idea}")

if __name__ == "__main__":
    test_seo_service()