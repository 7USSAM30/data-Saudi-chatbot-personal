import os
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Adjust the import path for answer_agent
from agents.answer_agent import answer_user_question_async 
from pipeline import main as run_pipeline

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
        "https://front-bujdweef6-hussams-projects-f4dd66f7.vercel.app",  # Your current Vercel URL
        "https://datasaudi-chatbot.vercel.app"  # Your specific Vercel URL
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
        data = await request.json()
        question = data.get("question")
        
        if not question:
            return JSONResponse(status_code=400, content={"error": "Question is required."})
            
        logger.info(f"Received question: {question}")
        
        # Test environment variables first
        openai_key = os.getenv("OPENAI_API_KEY")
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_key = os.getenv("WEAVIATE_API_KEY")
        
        logger.info(f"OpenAI API Key present: {bool(openai_key)}")
        logger.info(f"Weaviate URL present: {bool(weaviate_url)}")
        logger.info(f"Weaviate API Key present: {bool(weaviate_key)}")
        
        if not openai_key:
            return JSONResponse(status_code=500, content={"error": "OpenAI API key not configured."})
        
        if not weaviate_url or not weaviate_key:
            return JSONResponse(status_code=500, content={"error": "Weaviate configuration missing."})
        
        # Get the answer and sources from the agent
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Data Saudi Chatbot backend.")
    parser.add_argument('--run-pipeline', action='store_true', help='Run the data processing pipeline instead of the API.')
    args = parser.parse_args()

    if args.run_pipeline:
        logger.info("Starting the data processing pipeline...")
        asyncio.run(run_pipeline())
        logger.info("Pipeline finished.")
    else:
        logger.info("Starting the FastAPI server...")
        run_api()
