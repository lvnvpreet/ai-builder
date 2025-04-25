import json
import os

def generate_test_data():
    """Generate test data for SEO analysis."""
    
    # Sample content for testing
    test_content = {
        "technology": """
        The Future of Artificial Intelligence in Technology
        
        Artificial Intelligence (AI) is revolutionizing the technology sector. 
        From machine learning algorithms to neural networks, AI is transforming 
        how we interact with technology. This comprehensive guide explores the 
        latest developments in AI technology and its impact on various industries.
        
        Key areas covered:
        1. Machine Learning fundamentals
        2. Neural Networks and Deep Learning
        3. Natural Language Processing
        4. Computer Vision applications
        5. AI Ethics and Governance
        
        As technology continues to evolve, AI remains at the forefront of innovation...
        """,
        
        "marketing": """
        Digital Marketing Strategies for 2024
        
        In today's competitive landscape, digital marketing is essential for business success. 
        This guide covers proven strategies for increasing online visibility, engaging 
        customers, and driving conversions through digital channels.
        
        Topics include:
        - Search Engine Optimization (SEO)
        - Content Marketing
        - Social Media Marketing
        - Email Marketing
        - Pay-Per-Click Advertising
        
        Learn how to create an integrated digital marketing strategy that delivers results...
        """,
        
        "ecommerce": """
        Building a Successful E-commerce Business
        
        E-commerce has transformed retail, offering unprecedented opportunities for 
        entrepreneurs. This guide provides insights into launching and scaling an 
        online store, from platform selection to customer acquisition.
        
        Essential components:
        1. Choosing the right e-commerce platform
        2. Product sourcing and inventory management
        3. Payment gateway integration
        4. Shipping and fulfillment
        5. Customer service excellence
        
        Discover the strategies that successful e-commerce businesses use to thrive...
        """
    }
    
    # Sample competitor URLs for testing
    test_competitors = {
        "technology": [
            "https://techcrunch.com",
            "https://wired.com",
            "https://thenextweb.com"
        ],
        "marketing": [
            "https://hubspot.com/marketing",
            "https://neilpatel.com",
            "https://searchenginejournal.com"
        ],
        "ecommerce": [
            "https://shopify.com/blog",
            "https://bigcommerce.com/blog",
            "https://woocommerce.com/posts"
        ]
    }
    
    # Sample keywords for testing
    test_keywords = {
        "technology": ["AI", "machine learning", "technology", "innovation", "artificial intelligence"],
        "marketing": ["digital marketing", "SEO", "content marketing", "social media", "marketing strategy"],
        "ecommerce": ["online store", "e-commerce", "shopping cart", "payment gateway", "inventory management"]
    }
    
    # Create test data directory
    os.makedirs("tests/data", exist_ok=True)
    
    # Save test data
    with open("tests/data/test_content.json", "w") as f:
        json.dump(test_content, f, indent=2)
    
    with open("tests/data/test_competitors.json", "w") as f:
        json.dump(test_competitors, f, indent=2)
    
    with open("tests/data/test_keywords.json", "w") as f:
        json.dump(test_keywords, f, indent=2)
    
    print("Test data generated successfully!")

if __name__ == "__main__":
    generate_test_data()