import os
import uvicorn
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI()

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "DataSaudi Chatbot API is running"}

@app.get("/test")
async def test():
    """Simple test endpoint."""
    return {"message": "Test endpoint working", "timestamp": "2025-09-15"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
