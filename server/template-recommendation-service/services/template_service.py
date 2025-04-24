import os
import json
import logging
from typing import Dict, List, Any
import config

logger = logging.getLogger("template_recommender.template_service")

class TemplateService:
    """Service for managing template data."""
    
    def __init__(self):
        """Initialize the template service."""
        self.templates = {}
        self.industry_mappings = {}
        
    def initialize(self):
        """Load template data and industry mappings."""
        self._load_templates()
        self._load_industry_mappings()
        
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all templates."""
        return self.templates
        
    def get_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """Get a template by ID."""
        return self.templates.get(template_id, {})
        
    def get_templates_for_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get templates suitable for a specific industry."""
        if not industry:
            return []
            
        industry_lower = industry.lower()
        
        # First try exact match in mappings
        if industry_lower in self.industry_mappings:
            template_ids = self.industry_mappings[industry_lower]
            return [self.templates[tid] for tid in template_ids if tid in self.templates]
        
        # Then try matching templates directly
        matching_templates = []
        for template_id, template_data in self.templates.items():
            template_industries = [i.lower() for i in template_data.get('industries', [])]
            if industry_lower in template_industries:
                matching_templates.append(template_data)
                
        return matching_templates
        
    def _load_templates(self):
        """Load templates from the JSON file."""
        try:
            if not os.path.exists(config.TEMPLATES_PATH):
                logger.warning(f"Templates file not found: {config.TEMPLATES_PATH}")
                self._create_default_templates()
                return
                
            with open(config.TEMPLATES_PATH, 'r') as f:
                self.templates = json.load(f)
                
            logger.info(f"Loaded {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            self._create_default_templates()
            
    def _load_industry_mappings(self):
        """Load industry mappings from the JSON file."""
        try:
            if not os.path.exists(config.INDUSTRY_MAPPINGS_PATH):
                logger.warning(f"Industry mappings file not found: {config.INDUSTRY_MAPPINGS_PATH}")
                self._create_default_industry_mappings()
                return
                
            with open(config.INDUSTRY_MAPPINGS_PATH, 'r') as f:
                self.industry_mappings = json.load(f)
                
            logger.info(f"Loaded industry mappings for {len(self.industry_mappings)} industries")
        except Exception as e:
            logger.error(f"Error loading industry mappings: {str(e)}")
            self._create_default_industry_mappings()
            
    def _create_default_templates(self):
        """Create and save default templates if none exist."""
        logger.info("Creating default templates")
        
        self.templates = {
            "template_1": {
                "name": "Modern Business",
                "description": "A sleek, professional template for modern businesses featuring a clean design and impressive hero section.",
                "industries": ["technology", "consulting", "professional_services"],
                "style": "modern",
                "features": ["responsive design", "contact form", "testimonials section", "services showcase"],
                "target_audience": ["professionals", "corporate clients"],
                "previewUrl": "/previews/template_1.png"
            },
            "template_2": {
                "name": "E-commerce Essential",
                "description": "A conversion-focused template for online stores with product galleries and checkout integration.",
                "industries": ["ecommerce", "retail", "fashion"],
                "style": "minimal",
                "features": ["product showcase", "shopping cart", "category navigation", "search functionality"],
                "target_audience": ["shoppers", "online consumers"],
                "previewUrl": "/previews/template_2.png"
            },
            "template_3": {
                "name": "Creative Portfolio",
                "description": "An artistic template for showcasing creative work with stunning visuals and project galleries.",
                "industries": ["creative", "portfolio", "photography", "design"],
                "style": "artistic",
                "features": ["gallery views", "project showcase", "animation effects", "minimal text focus"],
                "target_audience": ["creatives", "artists", "designers"],
                "previewUrl": "/previews/template_3.png" 
            },
            "template_4": {
                "name": "Restaurant & Cafe",
                "description": "A mouth-watering template for restaurants, cafes, and food businesses, featuring menu displays and reservation systems.",
                "industries": ["restaurant", "cafe", "food_service", "hospitality"],
                "style": "warm",
                "features": ["menu display", "reservation system", "location map", "food gallery"],
                "target_audience": ["diners", "food enthusiasts"],
                "previewUrl": "/previews/template_4.png"
            },
            "template_5": {
                "name": "Professional Blog",
                "description": "A content-focused template for bloggers and content creators with excellent readability and sharing features.",
                "industries": ["blog", "media", "publishing", "content_creation"],
                "style": "clean",
                "features": ["article layout", "categories", "author profiles", "social sharing"],
                "target_audience": ["readers", "content consumers"],
                "previewUrl": "/previews/template_5.png"
            }
        }
        
        # Save to file
        os.makedirs(os.path.dirname(config.TEMPLATES_PATH), exist_ok=True)
        with open(config.TEMPLATES_PATH, 'w') as f:
            json.dump(self.templates, f, indent=2)
            
        logger.info(f"Created and saved {len(self.templates)} default templates")
            
    def _create_default_industry_mappings(self):
        """Create and save default industry mappings if none exist."""
        logger.info("Creating default industry mappings")
        
        self.industry_mappings = {
            "technology": ["template_1"],
            "software": ["template_1"],
            "consulting": ["template_1"],
            "professional_services": ["template_1"],
            
            "ecommerce": ["template_2"],
            "retail": ["template_2"],
            "fashion": ["template_2"],
            
            "creative": ["template_3"],
            "portfolio": ["template_3"],
            "photography": ["template_3"],
            "design": ["template_3"],
            
            "restaurant": ["template_4"],
            "cafe": ["template_4"],
            "food_service": ["template_4"],
            "hospitality": ["template_4"],
            
            "blog": ["template_5"],
            "media": ["template_5"],
            "publishing": ["template_5"],
            "content_creation": ["template_5"]
        }
        
        # Save to file
        os.makedirs(os.path.dirname(config.INDUSTRY_MAPPINGS_PATH), exist_ok=True)
        with open(config.INDUSTRY_MAPPINGS_PATH, 'w') as f:
            json.dump(self.industry_mappings, f, indent=2)
            
        logger.info(f"Created and saved mappings for {len(self.industry_mappings)} industries")