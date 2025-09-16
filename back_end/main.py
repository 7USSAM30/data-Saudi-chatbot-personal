import os
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Cannot be True with allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

@app.get("/test")
async def test():
    """Simple test endpoint."""
    return {"message": "Test endpoint working", "timestamp": "2025-09-15"}

@app.post("/api/pipeline")
async def run_pipeline():
    """Run the data processing pipeline to populate Weaviate."""
    try:
        from back_end.pipeline import main as run_pipeline_main
        logger.info("Starting data processing pipeline...")
        await run_pipeline_main()
        return JSONResponse(content={"status": "success", "message": "Pipeline completed successfully"})
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return JSONResponse(status_code=500, content={"error": f"Pipeline failed: {str(e)}"})

@app.post("/api/ask")
async def ask(request: Request):
    try:
        body = await request.body()
        if not body:
            return JSONResponse(status_code=400, content={"error": "Request body is required."})
        
        try:
            data = await request.json()
        except Exception as json_error:
            return JSONResponse(status_code=400, content={"error": f"Invalid JSON: {str(json_error)}"})
        
        question = data.get("question")
        
        if not question:
            return JSONResponse(status_code=400, content={"error": "Question is required."})
            
        logger.info(f"Received question: {question}")
        
        # Try to import and use the agent system
        try:
            from back_end.agents.answer_agent import answer_user_question_async
            result = await answer_user_question_async(question)
            
            logger.info(f"Answer: {result['answer']}")
            logger.info(f"Sources: {result['sources']}")
            
            return JSONResponse(content={
                "answer": result["answer"],
                "context": result["sources"]
            })
        except ImportError as import_error:
            logger.error(f"Agent import failed: {import_error}")
            return JSONResponse(content={
                "answer": f"I received your question: '{question}'. The agent system is currently unavailable due to missing dependencies. Please check the backend logs for details.",
                "context": ["Fallback response - agent import failed", f"Error: {str(import_error)}"]
            })
        except Exception as agent_error:
            logger.error(f"Agent error: {agent_error}")
            return JSONResponse(content={
                "answer": f"I received your question: '{question}'. The agent system encountered an error. Please check the backend logs for details.",
                "context": ["Fallback response - agent error", f"Error: {str(agent_error)}"]
            })
        
    except Exception as e:
        logger.error(f"An error occurred in /api/ask: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"An internal server error occurred: {str(e)}"})

def run_api():
    """Runs the FastAPI server."""
    port = int(os.getenv("PORT", 8000))  # Use Railway's PORT or default to 8000
    logger.info(f"Starting server on port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    logger.info("=== DataSaudi Chatbot Backend Starting ===")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    
    import argparse
    parser = argparse.ArgumentParser(description="Run the Data Saudi Chatbot backend.")
    parser.add_argument('--run-pipeline', action='store_true', help='Run the data processing pipeline instead of the API.')
    args = parser.parse_args()

    if args.run_pipeline:
        try:
            from back_end.pipeline import main as run_pipeline
            logger.info("Starting the data processing pipeline...")
            asyncio.run(run_pipeline())
            logger.info("Pipeline finished.")
        except ImportError as e:
            logger.error(f"Pipeline import failed: {e}")
            exit(1)
    else:
        logger.info("Starting the FastAPI server...")
        try:
            run_api()
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise