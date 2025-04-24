import os
import uuid
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import json
from datetime import datetime

# Import our custom modules
from models import OrchestrationInput, OrchestrationOutput, OrchestrationStatus
from orchestrator import Orchestrator
from caching import ResultCache
from job_manager import JobManager
from utils import setup_logging, check_service_health, request_id_var, session_id_var
from redis_client import RedisClient

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize Redis client
redis_client = RedisClient()

# Initialize services
orchestrator = Orchestrator(redis_client)
cache = ResultCache(redis_client)
job_manager = JobManager(redis_client)

app = FastAPI(
    title="AI Orchestrator Service",
    description="Coordinates AI subsystems (Template Recommendation, RAG, Content Generation, Design Rules).",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request tracking and metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID and store in context
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract session ID if present in headers or path params
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            session_id_var.set(session_id)
        
        # Timing metrics
        start_time = time.time()
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log request completion
        logger.info(
            f"Request completed: {request.method} {request.url.path}", 
            extra={
                "context": {
                    "request_id": request_id,
                    "session_id": session_id_var.get(),
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "status_code": response.status_code
                }
            }
        )
        
        # Return response
        return response

# Add middleware to app
app.add_middleware(MetricsMiddleware)

# Dependency for logging context
async def get_logging_context():
    return {
        "request_id": request_id_var.get(),
        "session_id": session_id_var.get()
    }

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "AI Orchestrator Service is running!"}

@app.get("/health")
async def health_check():
    """Detailed health check with dependency status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check each dependent service
    template_service_url = os.getenv("TEMPLATE_RECOMMENDER_URL", "http://localhost:3007")
    rag_service_url = os.getenv("RAG_SERVICE_URL", "http://localhost:3008")
    content_generator_url = os.getenv("CONTENT_GENERATOR_URL", "http://localhost:3009")
    design_rules_url = os.getenv("DESIGN_RULES_URL", "http://localhost:3010")
    
    # Check Redis connection
    health_status["dependencies"]["redis"] = {
        "status": "healthy" if redis_client.connected else "unhealthy"
    }
    
    # Check each service
    health_status["dependencies"]["template_service"] = await check_service_health(template_service_url)
    health_status["dependencies"]["rag_service"] = await check_service_health(rag_service_url)
    health_status["dependencies"]["content_generator"] = await check_service_health(content_generator_url)
    health_status["dependencies"]["design_rules"] = await check_service_health(design_rules_url)
    
    # Overall health is degraded if any dependency is unhealthy
    if any(dep.get("status") == "unhealthy" for dep in health_status["dependencies"].values()):
        health_status["status"] = "degraded"
        
    return health_status

@app.post("/orchestrate", response_model=OrchestrationOutput)
async def orchestrate_ai_process(
    data: OrchestrationInput,
    background_tasks: BackgroundTasks,
    logging_context: dict = Depends(get_logging_context)
):
    """
    Main orchestration endpoint that coordinates AI subsystems.
    For long-running tasks, returns immediately with a job ID and processes in background.
    """
    logger.info(
        f"Starting orchestration for session {data.sessionId}",
        extra={"context": {**logging_context, "input_data": str(data)[:100] + "..."}}
    )
    
    # Check if we have a cached result
    cache_key = cache.generate_cache_key(data.dict())
    cached_result = await cache.get("orchestrate", cache_key)
    if cached_result:
        logger.info(f"Returning cached result for session {data.sessionId}")
        return OrchestrationOutput(**cached_result)
    
    # For quick operations (<2 seconds), do them immediately
    # For longer operations, use background tasks
    
    # Create a job for tracking
    job_id = await job_manager.enqueue_job("orchestrate", data.dict())
    
    # Start the orchestration process in the background
    background_tasks.add_task(
        process_orchestration_job,
        job_id=job_id,
        data=data,
        logging_context=logging_context
    )
    
    # Return immediately with job information
    return OrchestrationOutput(
        sessionId=data.sessionId,
        status=OrchestrationStatus.PROCESSING,
        progress=0.1,
        website_generation_data={"job_id": job_id}
    )

async def process_orchestration_job(job_id: str, data: OrchestrationInput, logging_context: dict):
    """Background task to handle orchestration process."""
    try:
        # Update job status to processing
        await job_manager.update_job_status(job_id, "processing")
        
        # Run the orchestration
        result = await orchestrator.orchestrate(data)
        
        # Cache successful results
        if result.status == OrchestrationStatus.COMPLETED:
            cache_key = cache.generate_cache_key(data.dict())
            await cache.set("orchestrate", cache_key, result.dict())
        
        # Update job with result
        await job_manager.update_job_status(
            job_id,
            "completed" if result.status == OrchestrationStatus.COMPLETED else "failed",
            result=result.dict()
        )
        
        logger.info(
            f"Completed orchestration job {job_id} for session {data.sessionId} with status {result.status}",
            extra={"context": logging_context}
        )
    except Exception as e:
        logger.error(
            f"Error processing orchestration job {job_id}: {str(e)}",
            extra={"context": {**logging_context, "error": str(e)}}
        )
        await job_manager.update_job_status(job_id, "failed", error=str(e))

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a job."""
    job = await job_manager.get_job_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    import time
    port = int(os.getenv("PORT", "3011")) # Default to port 3011 for orchestrator
    print(f"Starting AI Orchestrator Service on http://localhost:{port}")
    
    # Connect to Redis before starting
    asyncio.run(redis_client.connect())
    
    # Use reload=True for development
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)