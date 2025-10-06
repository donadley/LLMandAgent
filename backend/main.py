from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from agents.agent_manager import AgentManager
from utils.logger import setup_logger

# Set up logger
logger = setup_logger("api")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    callback_manager=callback_manager,
    temperature=0.7,
    max_tokens=2000,
    verbose=True,
)

# Initialize Agent Manager
agent_manager = AgentManager(llm)

class Query(BaseModel):
    text: str
    parameters: Dict[str, Any] = {}
    use_agent: bool = False

@app.post("/api/chat")
async def chat(query: Query):
    logger.info(f"Received chat request: {query.text[:100]}...")
    try:
        if query.use_agent:
            logger.info("Using agent for processing")
            response = await agent_manager.process_message(query.text)
        else:
            logger.info("Using direct LLM response")
            response = llm(query.text)
        logger.info("Successfully processed chat request")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}