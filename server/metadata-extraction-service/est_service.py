# server/metadata-extraction-service/test_service.py
import requests
import json

def test_extraction():
    """Test the enhanced metadata extraction service."""
    
    # Test text with various structures
    test_text = """
    Our B2B SaaS platform uses React and Node.js to provide enterprise solutions.
    
    # Main Features
    
    1. Real-time analytics dashboard
    2. Custom reporting tools
    3. API integration capabilities
    
    ## Technology Stack
    
    - Frontend: React, TypeScript
    - Backend: Node.js, Express
    - Database: PostgreSQL
    
    The platform targets SMB markets with a subscription pricing model starting at $99/month.
    """
    
    url = "http://localhost:3004/extract"
    
    payload = {
        "text": test_text,
        "extract_entities": True,
        "extract_keywords": True,
        "extract_topics": True,
        "extract_structure": True,
        "topic_modeling_method": "lda",
        "num_topics": 3,
        "document_format": "markdown",
        "use_custom_ner": True
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print("\n=== Extraction Results ===")
    
    print("\n1. Standard Entities:")
    for entity in result.get("entities", [])[:5]:
        print(f"  - {entity['text']} ({entity['label']})")
    
    print("\n2. Custom Entities:")
    for entity in result.get("custom_entities", []):
        print(f"  - {entity['text']} ({entity['label']})")
    
    print("\n3. Pattern Matches:")
    for match in result.get("pattern_matches", []):
        print(f"  - {match['text']} ({match['label']})")
    
    print("\n4. Keywords:")
    print(f"  {', '.join(result.get('keywords', [])[:10])}")
    
    print("\n5. Topics:")
    for topic in result.get("topics", []):
        print(f"  Topic {topic['topic_id']}: {', '.join(topic['words'][:5])}")
    
    print("\n6. Document Structure:")
    structure = result.get("structure", {})
    print(f"  Headings: {len(structure.get('headings', []))}")
    print(f"  Sections: {len(structure.get('sections', []))}")
    print(f"  Lists: {len(structure.get('lists', []))}")
    print(f"  Complexity Score: {structure.get('complexity_metrics', {}).get('complexity_score', 0)}")

if __name__ == "__main__":
    test_extraction()