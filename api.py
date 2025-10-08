from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import asyncio
import time

# Create FastAPI app instance
app = FastAPI(
    title="MQTT API",
    description="A simple FastAPI application with one endpoint",
    version="1.0.0"
)

# Pydantic model for request body (optional)
class MessageModel(BaseModel):
    message: str
    sender: str = "anonymous"

# Root endpoint
@app.get("/")
async def read_root() -> Dict[str, str]:
    """
    Root endpoint that returns a welcome message.
    """
    # Simulate processing time (1 second delay)
    await asyncio.sleep(1.0)
    
    return {
        "message": "Welcome to the MQTT API!", 
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    """
    # Simulate processing time (0.5 second delay)
    await asyncio.sleep(0.5)
    
    return {"status": "healthy", "service": "MQTT API"}

# POST endpoint example
@app.post("/send")
async def send_message(message: MessageModel) -> Dict[str, Any]:
    """
    Endpoint to send a message (example endpoint).
    """

    print(f"Received message from {message.sender}: {message.message}")

    # Simulate processing time (5 seconds delay for message processing simulation)
    await asyncio.sleep(5.0)
    
    return {
        "status": "success",
        "received_message": message.message,
        "sender": message.sender,
        "timestamp": time.time()
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run( 
        "api:app", 
        host="0.0.0.0", 
        port=8009, 
        reload=False
    )
