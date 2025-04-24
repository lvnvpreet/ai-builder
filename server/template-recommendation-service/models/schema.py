from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ProcessedInput(BaseModel):
    business_name: str
    industry: str
    description: str
    target_audience: List[str] = []
    unique_selling_points: List[str] = []
    competitor_urls: List[str] = []

class RecommendationInput(BaseModel):
    processed_input: Dict[str, Any]
    sessionId: str

class TemplateRecommendation(BaseModel):
    templateId: str
    score: float
    matchReason: Optional[str] = None
    previewUrl: Optional[str] = None
    features: List[str] = []
    
class RecommendationOutput(BaseModel):
    sessionId: str
    recommendations: List[TemplateRecommendation] = []