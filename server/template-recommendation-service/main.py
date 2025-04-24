import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import logging
from models.schema import RecommendationInput, RecommendationOutput
from services.recommendation_service import RecommendationService

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("template_recommender")

# Initialize the FastAPI app
app = FastAPI(
    title="Template Recommendation Service",
    description="Recommends website templates based on user input using pretrained models.",
    version="1.0.0"
)

# Initialize recommendation service
recommendation_service = RecommendationService()

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Loading recommendation models and data...")
    recommendation_service.initialize()
    logger.info("Recommendation service initialized successfully")

@app.get("/")
async def read_root():
    """Basic health check endpoint."""
    return {"message": "Template Recommendation Service is running!"}

@app.post("/recommend-templates", response_model=RecommendationOutput)
async def recommend_templates(data: RecommendationInput):
    """
    Generate template recommendations based on business data.
    
    Uses a pretrained sentence transformer model to find semantic matches
    between business descriptions and template characteristics.
    """
    logger.info(f"Received request to recommend templates for session: {data.sessionId}")
    
    try:
        # Get recommendations
        recommendations = recommendation_service.get_recommendations(
            business_description=data.processed_input.get("description", ""),
            industry=data.processed_input.get("industry", ""),
            business_name=data.processed_input.get("business_name", ""),
            target_audience=data.processed_input.get("target_audience", []),
            unique_selling_points=data.processed_input.get("unique_selling_points", []),
            top_k=int(os.getenv("TOP_K_RECOMMENDATIONS", "5"))
        )
        
        return RecommendationOutput(
            sessionId=data.sessionId,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3007"))
    logger.info(f"Starting Template Recommendation Service on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)