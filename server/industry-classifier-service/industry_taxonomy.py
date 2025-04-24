# server/industry-classifier-service/industry_taxonomy.py
from typing import Dict, List, Set, Optional
import json
import os

class IndustryTaxonomy:
    """Hierarchical industry taxonomy with relationships."""
    
    def __init__(self):
        self.taxonomy: Dict[str, Dict] = {}
        self.load_taxonomy()
    
    def load_taxonomy(self, path: str = "data/industry_taxonomy.json"):
        """Load taxonomy from JSON file."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.taxonomy = json.load(f)
        else:
            self.create_default_taxonomy()
            self.save_taxonomy(path)
    
    def create_default_taxonomy(self):
        """Create comprehensive industry taxonomy."""
        self.taxonomy = {
            "technology": {
                "display_name": "Technology",
                "subcategories": {
                    "software": {
                        "display_name": "Software Development",
                        "keywords": ["software", "programming", "coding", "development"],
                        "subtypes": ["SaaS", "Enterprise", "Mobile Apps", "Web Development"]
                    },
                    "hardware": {
                        "display_name": "Hardware",
                        "keywords": ["hardware", "electronics", "devices"],
                        "subtypes": ["Consumer Electronics", "Industrial", "Components"]
                    },
                    "ai_ml": {
                        "display_name": "AI & Machine Learning",
                        "keywords": ["artificial intelligence", "machine learning", "ai", "ml"],
                        "subtypes": ["Computer Vision", "NLP", "Robotics", "Data Science"]
                    }
                }
            },
            "healthcare": {
                "display_name": "Healthcare",
                "subcategories": {
                    "medical_services": {
                        "display_name": "Medical Services",
                        "keywords": ["medical", "clinic", "hospital", "healthcare"],
                        "subtypes": ["Hospitals", "Clinics", "Specialized Care", "Telemedicine"]
                    },
                    "pharmaceutical": {
                        "display_name": "Pharmaceutical",
                        "keywords": ["pharma", "drugs", "medicine", "pharmaceutical"],
                        "subtypes": ["Drug Manufacturing", "Research", "Distribution"]
                    },
                    "medical_devices": {
                        "display_name": "Medical Devices",
                        "keywords": ["medical devices", "equipment", "diagnostic"],
                        "subtypes": ["Diagnostic", "Therapeutic", "Monitoring"]
                    }
                }
            },
            "finance": {
                "display_name": "Finance",
                "subcategories": {
                    "banking": {
                        "display_name": "Banking",
                        "keywords": ["bank", "banking", "financial institution"],
                        "subtypes": ["Retail Banking", "Investment Banking", "Digital Banking"]
                    },
                    "fintech": {
                        "display_name": "FinTech",
                        "keywords": ["fintech", "financial technology", "payments"],
                        "subtypes": ["Payments", "Lending", "Blockchain", "InsurTech"]
                    },
                    "investment": {
                        "display_name": "Investment",
                        "keywords": ["investment", "trading", "asset management"],
                        "subtypes": ["Asset Management", "Hedge Funds", "Private Equity"]
                    }
                }
            }
            # Add more industries...
        }
    
    def save_taxonomy(self, path: str):
        """Save taxonomy to JSON file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.taxonomy, f, indent=2)
    
    def get_all_industries(self) -> List[str]:
        """Get all industry names (main categories)."""
        return list(self.taxonomy.keys())
    
    def get_subcategories(self, industry: str) -> List[str]:
        """Get subcategories for an industry."""
        if industry in self.taxonomy:
            return list(self.taxonomy[industry].get("subcategories", {}).keys())
        return []
    
    def get_keywords(self, industry: str, subcategory: Optional[str] = None) -> List[str]:
        """Get keywords for industry or subcategory."""
        keywords = []
        if industry in self.taxonomy:
            if subcategory and subcategory in self.taxonomy[industry].get("subcategories", {}):
                keywords = self.taxonomy[industry]["subcategories"][subcategory].get("keywords", [])
            else:
                # Collect keywords from all subcategories
                for subcat in self.taxonomy[industry].get("subcategories", {}).values():
                    keywords.extend(subcat.get("keywords", []))
        return keywords
    
    def get_hierarchy_path(self, industry: str, subcategory: Optional[str] = None) -> List[str]:
        """Get full hierarchy path."""
        path = []
        if industry in self.taxonomy:
            path.append(self.taxonomy[industry]["display_name"])
            if subcategory and subcategory in self.taxonomy[industry].get("subcategories", {}):
                path.append(self.taxonomy[industry]["subcategories"][subcategory]["display_name"])
        return path