# server/industry-classifier-service/test_classifier.py
import requests
import json

def test_classifier():
    """Test the enhanced industry classifier."""
    
    test_cases = [
        {
            "description": "We are a fintech startup developing blockchain-based payment solutions for small businesses.",
            "expected_primary": "finance",
            "expected_secondary": ["technology"]
        },
        {
            "description": "Our company manufactures medical diagnostic equipment with AI-powered analysis capabilities.",
            "expected_primary": "healthcare",
            "expected_secondary": ["technology"]
        },
        {
            "description": "We provide cloud-based SaaS solutions for enterprise resource planning and customer relationship management.",
            "expected_primary": "technology",
            "expected_secondary": ["software"]
        }
    ]
    
    url = "http://localhost:3005/classify"
    
    for i, test_case in enumerate(test_cases):
        payload = {
            "business_description": test_case["description"],
            "confidence_threshold": 0.3,
            "max_labels": 3,
            "include_subcategories": True
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        print(f"\nTest Case {i+1}:")
        print(f"Description: {test_case['description']}")
        print(f"Primary Industry: {result['primary_industry']['industry']} "
              f"(confidence: {result['primary_industry']['confidence']:.2f})")
        
        if result['secondary_industries']:
            print("Secondary Industries:")
            for secondary in result['secondary_industries']:
                print(f"  - {secondary['industry']} (confidence: {secondary['confidence']:.2f})")
        
        if result['primary_industry'].get('subcategories'):
            print("Subcategories:")
            for subcat in result['primary_industry']['subcategories']:
                print(f"  - {subcat['subcategory']} (confidence: {subcat['confidence']:.2f})")
        
        print("-" * 50)

if __name__ == "__main__":
    test_classifier()