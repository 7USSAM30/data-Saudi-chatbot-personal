import os
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Adjust the import path for answer_agent - with error handling
try:
    from agents.answer_agent import answer_user_question_async 
    from pipeline import main as run_pipeline
    logger.info("Successfully imported agent modules")
except ImportError as e:
    logger.error(f"Failed to import agent modules: {e}")
    # Set fallback functions
    answer_user_question_async = None
    run_pipeline = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
        "https://*.railway.app",  # Railway deployments
        "https://data-saudi-chatbot-personal.vercel.app",  # Your current Vercel URL
        "https://data-saudi-chatbot-personal-git-main-hussams-projects-f4dd66f7.vercel.app",  # Alternative Vercel URL
        "https://data-saudi-chatbot-personal-fp9680dv5-hussams-projects-f4dd66f7.vercel.app",  # Alternative Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "DataSaudi Chatbot API is running"}

@app.get("/health")
async def health():
    """Alternative health check endpoint."""
    return {"status": "healthy", "service": "datasaudi-chatbot"}

@app.post("/api/ask")
async def ask(request: Request):
    try:
        # Check if request has body
        body = await request.body()
        if not body:
            return JSONResponse(status_code=400, content={"error": "Request body is required."})
        
        # Parse JSON
        try:
            data = await request.json()
        except Exception as json_error:
            return JSONResponse(status_code=400, content={"error": f"Invalid JSON: {str(json_error)}"})
        
        question = data.get("question")
        
        if not question:
            return JSONResponse(status_code=400, content={"error": "Question is required."})
            
        logger.info(f"Received question: {question}")
        
        # Get the answer and sources from the agent
        if answer_user_question_async is None:
            logger.warning("Agent module not available, using fallback response")
            return JSONResponse(content={
                "answer": f"I received your question: '{question}'. The agent system is currently unavailable, but the API is working! Please check the backend logs.",
                "context": ["Fallback response - agent module unavailable"]
            })
        
        result = await answer_user_question_async(question)
        
        logger.info(f"Answer: {result['answer']}")
        logger.info(f"Sources: {result['sources']}")
        
        return JSONResponse(content={
            "answer": result["answer"],
            "context": result["sources"]
        })
        
    except Exception as e:
        logger.error(f"An error occurred in /api/ask: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"An internal server error occurred: {str(e)}"})

def run_api():
    """Runs the FastAPI server."""
    port = int(os.getenv("PORT", 8000))  # Use Railway's PORT or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Data Saudi Chatbot backend.")
    parser.add_argument('--run-pipeline', action='store_true', help='Run the data processing pipeline instead of the API.')
    args = parser.parse_args()

    if args.run_pipeline:
        if run_pipeline is None:
            logger.error("Pipeline module not available")
            exit(1)
        logger.info("Starting the data processing pipeline...")
        asyncio.run(run_pipeline())
        logger.info("Pipeline finished.")
    else:
        logger.info("Starting the FastAPI server...")
        run_api()
