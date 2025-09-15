import os
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.railway.app",
        "https://data-saudi-chatbot-personal.vercel.app",
        "https://data-saudi-chatbot-personal-git-main-hussams-projects-f4dd66f7.vercel.app",
        "https://data-saudi-chatbot-personal-fp9680dv5-hussams-projects-f4dd66f7.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "DataSaudi Chatbot API is running - MINIMAL VERSION"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "datasaudi-chatbot-minimal"}

# Simple API endpoint
@app.post("/api/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "No question provided")
        
        logger.info(f"Received question: {question}")
        
        return JSONResponse(content={
            "answer": f"Hello! I received your question: '{question}'. This is the minimal backend working! 🎉",
            "context": ["Minimal backend response"]
        })
        
    except Exception as e:
        logger.error(f"Error in /api/ask: {e}")
        return JSONResponse(status_code=500, content={"error": f"Internal error: {str(e)}"})

# Run function
def run_api():
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    logger.info("Starting minimal FastAPI server...")
    run_api()
