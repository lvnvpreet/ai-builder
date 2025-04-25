# Update server/industry-classifier-service/main.py
import os
import torch
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import json
import numpy as np
from industry_taxonomy import IndustryTaxonomy

load_dotenv()

app = FastAPI(
    title="Industry Classifier Service",
    description="Classifies business types with multi-label support and hierarchical taxonomy.",
    version="2.0.0"
)

# Global variables
taxonomy = IndustryTaxonomy()
custom_model = None
custom_tokenizer = None
zero_shot_classifier = None
label_mapping = None

# Load models on startup
@app.on_event("startup")
async def load_models():
    global custom_model, custom_tokenizer, zero_shot_classifier, label_mapping
    
    # Load custom model if available
    custom_model_path = os.getenv("CUSTOM_MODEL_PATH", "models/custom_industry_classifier")
    if os.path.exists(custom_model_path):
        try:
            custom_model = AutoModelForSequenceClassification.from_pretrained(custom_model_path)
            custom_tokenizer = AutoTokenizer.from_pretrained(custom_model_path)
            
            # Load label mapping
            with open(f"{custom_model_path}/label_mapping.json", 'r') as f:
                label_mapping = json.load(f)
            
            print(f"Loaded custom model from {custom_model_path}")
        except Exception as e:
            print(f"Error loading custom model: {e}")
    
    # Load zero-shot classifier as fallback
    model_name = os.getenv("ZERO_SHOT_MODEL", "facebook/bart-large-mnli")
    try:
        zero_shot_classifier = pipeline("zero-shot-classification", model=model_name)
        print(f"Loaded zero-shot classifier: {model_name}")
    except Exception as e:
        print(f"Error loading zero-shot classifier: {e}")

# Data Models
class ClassificationInput(BaseModel):
    business_description: str
    use_custom_model: bool = True  # Whether to use custom model if available
    confidence_threshold: float = 0.3  # Threshold for multi-label classification
    max_labels: int = 3  # Maximum number of labels to return
    include_subcategories: bool = True  # Whether to include subcategory classification
    sessionId: Optional[str] = None

class IndustryPrediction(BaseModel):
    industry: str
    confidence: float
    subcategories: List[Dict[str, float]] = []
    keywords_matched: List[str] = []

class ClassificationOutput(BaseModel):
    primary_industry: IndustryPrediction
    secondary_industries: List[IndustryPrediction] = []
    confidence_scores: Dict[str, float] = {}
    classification_method: str  # "custom_model" or "zero_shot"

# Helper functions
def classify_with_custom_model(text: str, threshold: float, max_labels: int) -> List[Dict]:
    """Classify using custom trained model."""
    if not custom_model or not custom_tokenizer:
        raise ValueError("Custom model not available")
    
    # Tokenize input
    inputs = custom_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    # Get predictions
    with torch.no_grad():
        outputs = custom_model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
    
    # Convert to numpy for easier handling
    probs = probabilities.numpy()
    
    # Get labels above threshold
    indices = np.where(probs > threshold)[0]
    if len(indices) == 0:
        # If none above threshold, take the highest
        indices = [np.argmax(probs)]
    
    # Sort by probability and limit to max_labels
    sorted_indices = sorted(indices, key=lambda i: probs[i], reverse=True)[:max_labels]
    
    results = []
    for idx in sorted_indices:
        label_name = label_mapping[str(idx)]
        results.append({
            "industry": label_name,
            "confidence": float(probs[idx])
        })
    
    return results

def classify_with_zero_shot(text: str, threshold: float, max_labels: int) -> List[Dict]:
    """Classify using zero-shot classifier."""
    if not zero_shot_classifier:
        raise ValueError("Zero-shot classifier not available")
    
    # Get all industry labels from taxonomy
    candidate_labels = taxonomy.get_all_industries()
    
    # Perform classification
    result = zero_shot_classifier(text, candidate_labels, multi_label=True)
    
    # Filter by threshold and limit
    results = []
    for label, score in zip(result['labels'], result['scores']):
        if score > threshold:
            results.append({
                "industry": label,
                "confidence": score
            })
    
    return results[:max_labels]

def classify_subcategories(text: str, industry: str) -> List[Dict[str, float]]:
    """Classify subcategories for a given industry."""
    subcategories = taxonomy.get_subcategories(industry)
    if not subcategories or not zero_shot_classifier:
        return []
    
    result = zero_shot_classifier(text, subcategories, multi_label=True)
    
    # Return top 3 subcategories with scores
    subcategory_scores = []
    for subcat, score in zip(result['labels'][:3], result['scores'][:3]):
        if score > 0.2:  # Lower threshold for subcategories
            subcategory_scores.append({
                "subcategory": subcat,
                "confidence": score
            })
    
    return subcategory_scores

def match_keywords(text: str, industry: str) -> List[str]:
    """Find matching keywords in text for an industry."""
    keywords = taxonomy.get_keywords(industry)
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    return matched

# API Endpoints
@app.get("/")
async def read_root():
    """Basic health check endpoint."""
    return {
        "message": "Industry Classifier Service v2.0 is running!",
        "features": {
            "custom_model_available": custom_model is not None,
            "zero_shot_available": zero_shot_classifier is not None,
            "multi_label_support": True,
            "hierarchical_classification": True
        }
    }

@app.post("/classify", response_model=ClassificationOutput)
async def classify_industry(data: ClassificationInput):
    """
    Multi-label industry classification with subcategory support.
    """
    try:
        # Choose classification method
        if data.use_custom_model and custom_model:
            results = classify_with_custom_model(
                data.business_description,
                data.confidence_threshold,
                data.max_labels
            )
            method = "custom_model"
        else:
            results = classify_with_zero_shot(
                data.business_description,
                data.confidence_threshold,
                data.max_labels
            )
            method = "zero_shot"
        
        if not results:
            raise ValueError("No classification results")
        
        # Process primary industry
        primary = results[0]
        primary_prediction = IndustryPrediction(
            industry=primary["industry"],
            confidence=primary["confidence"]
        )
        
        # Get subcategories and keywords if requested
        if data.include_subcategories:
            primary_prediction.subcategories = classify_subcategories(
                data.business_description,
                primary["industry"]
            )
            primary_prediction.keywords_matched = match_keywords(
                data.business_description,
                primary["industry"]
            )
        
        # Process secondary industries
        secondary_predictions = []
        for result in results[1:]:
            prediction = IndustryPrediction(
                industry=result["industry"],
                confidence=result["confidence"]
            )
            
            if data.include_subcategories:
                prediction.subcategories = classify_subcategories(
                    data.business_description,
                    result["industry"]
                )
                prediction.keywords_matched = match_keywords(
                    data.business_description,
                    result["industry"]
                )
            
            secondary_predictions.append(prediction)
        
        # Create confidence scores dictionary
        confidence_scores = {r["industry"]: r["confidence"] for r in results}
        
        return ClassificationOutput(
            primary_industry=primary_prediction,
            secondary_industries=secondary_predictions,
            confidence_scores=confidence_scores,
            classification_method=method
        )
    
    except Exception as e:
        print(f"Error during classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/taxonomy")
async def get_taxonomy():
    """Get the complete industry taxonomy."""
    return taxonomy.taxonomy

@app.get("/industries/{industry}/subcategories")
async def get_industry_subcategories(industry: str):
    """Get subcategories for a specific industry."""
    subcategories = taxonomy.get_subcategories(industry)
    if not subcategories:
        raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found")
    return {"industry": industry, "subcategories": subcategories}

# Run the server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3005"))
    print(f"Starting Industry Classifier Service v2.0 on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)