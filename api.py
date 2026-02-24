import logging
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import chatbot_logic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LocalChatbotAPI")

app = FastAPI(title="Local Chatbot API", description="API for local Ollama chatbot")

class Message(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "qwen2.5vl:7b"

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify connectivity and logic availability.
    """
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/chat")
async def chat(request: ChatRequest, req_info: Request):
    """
    Chat endpoint.
    Accepts a list of messages and returns the assistant's response.
    """
    start_time = time.time()
    logger.info(f"Received chat request from {req_info.client.host} with {len(request.messages)} messages")
    
    try:
        # Convert Pydantic models to dictionaries for the logic function
        messages_data = [msg.model_dump() for msg in request.messages]
        
        # Get response generator
        response_generator = chatbot_logic.chat_with_model(messages_data, model=request.model)
        
        full_response = ""
        for chunk in response_generator:
            full_response += chunk
            
        if full_response.startswith("Error:"):
            logger.error(f"Logic returned error: {full_response}")
            raise HTTPException(status_code=500, detail=full_response)
            
        duration = time.time() - start_time
        logger.info(f"Successfully processed request in {duration:.2f}s")
        return {"role": "assistant", "content": full_response}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces (0.0.0.0) to allow LAN and ngrok access
    logger.info("Starting API server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
