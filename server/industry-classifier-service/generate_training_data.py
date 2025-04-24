# server/industry-classifier-service/generate_training_data.py
import pandas as pd
import random
from industry_taxonomy import IndustryTaxonomy
import os

def generate_training_data(num_samples: int = 1000, output_path: str = "data/industry_training_data.csv"):
    """Generate synthetic training data for industry classification."""
    
    taxonomy = IndustryTaxonomy()
    data = []
    
    # Templates for generating business descriptions
    templates = [
        "We are a {industry} company specializing in {subcategory}. Our services include {features}.",
        "As a leading {industry} business, we focus on {subcategory} solutions for {target}.",
        "Our {industry} firm provides innovative {subcategory} services with emphasis on {features}.",
        "{Company} is a {industry} organization dedicated to {subcategory} and {features}.",
        "Established in the {industry} sector, we offer comprehensive {subcategory} solutions.",
    ]
    
    company_names = ["TechCorp", "InnovateCo", "GlobalSolutions", "FutureTech", "SmartBiz"]
    targets = ["enterprises", "small businesses", "startups", "professionals", "consumers"]
    
    for industry, details in taxonomy.taxonomy.items():
        for subcategory, subdetails in details.get("subcategories", {}).items():
            # Generate multiple samples per subcategory
            for _ in range(num_samples // (len(taxonomy.taxonomy) * 3)):
                template = random.choice(templates)
                features = random.sample(subdetails.get("subtypes", []), min(2, len(subdetails.get("subtypes", []))))
                
                description = template.format(
                    industry=details["display_name"],
                    subcategory=subdetails["display_name"],
                    features=", ".join(features) if features else "various services",
                    target=random.choice(targets),
                    Company=random.choice(company_names)
                )
                
                data.append({
                    "text": description,
                    "industry": industry,
                    "subcategory": subcategory
                })
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} training samples and saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_training_data(num_samples=2000)