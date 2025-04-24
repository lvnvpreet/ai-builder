# server/metadata-extraction-service/custom_ner/data_generator.py
import json
import random

def generate_ner_training_data(output_path: str = "data/ner_training_data.json"):
    """Generate training data for custom NER."""
    
    # Templates and patterns for generating training data
    templates = [
        {
            "text": "Our {BUSINESS_MODEL} platform uses {TECH_STACK} and targets the {MARKET_SEGMENT} market.",
            "entity_types": ["BUSINESS_MODEL", "TECH_STACK", "MARKET_SEGMENT"]
        },
        {
            "text": "We offer a {PRICING_MODEL} pricing model for our {BUSINESS_MODEL} solution.",
            "entity_types": ["PRICING_MODEL", "BUSINESS_MODEL"]
        },
        {
            "text": "The platform is built with {TECH_STACK} and serves {MARKET_SEGMENT} clients.",
            "entity_types": ["TECH_STACK", "MARKET_SEGMENT"]
        }
    ]
    
    entity_values = {
        "BUSINESS_MODEL": ["B2B", "B2C", "SaaS", "marketplace", "subscription-based"],
        "TECH_STACK": ["React", "Angular", "Vue.js", "Django", "Node.js", "Python"],
        "MARKET_SEGMENT": ["enterprise", "SMB", "startup", "corporate", "consumer"],
        "PRICING_MODEL": ["freemium", "subscription", "pay-per-use", "one-time", "tiered"]
    }
    
    training_data = []
    
    for _ in range(500):  # Generate 500 examples
        template = random.choice(templates)
        text = template["text"]
        entities = []
        
        # Replace placeholders with actual values
        for entity_type in template["entity_types"]:
            value = random.choice(entity_values[entity_type])
            placeholder = f"{{{entity_type}}}"
            
            if placeholder in text:
                start_idx = text.index(placeholder)
                text = text.replace(placeholder, value, 1)
                end_idx = start_idx + len(value)
                entities.append([start_idx, end_idx, entity_type])
        
        training_data.append({
            "text": text,
            "entities": entities
        })
    
    # Save training data
    with open(output_path, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    return training_data