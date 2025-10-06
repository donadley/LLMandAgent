from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from langchain_community.llms import LlamaCpp
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

# Initialize LLMs from config
from models.configs.model_config import AVAILABLE_MODELS, ModelType

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Initialize general-purpose LLM (Mistral)
general_llm = LlamaCpp(
    model_path=AVAILABLE_MODELS[ModelType.GENERAL].model_path,
    callback_manager=callback_manager,
    temperature=AVAILABLE_MODELS[ModelType.GENERAL].temperature,
    max_tokens=AVAILABLE_MODELS[ModelType.GENERAL].max_tokens,
    verbose=True,
)

# Initialize code-specific LLM (CodeLlama)
code_llm = LlamaCpp(
    model_path=AVAILABLE_MODELS[ModelType.CODE].model_path,
    callback_manager=callback_manager,
    temperature=AVAILABLE_MODELS[ModelType.CODE].temperature,
    max_tokens=AVAILABLE_MODELS[ModelType.CODE].max_tokens,
    verbose=True,
)

# Initialize Agent Manager with general-purpose LLM
agent_manager = AgentManager(general_llm)

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
            # Use code_llm for code-related queries, general_llm for everything else
            if any(code_indicator in query.text.lower() for code_indicator in ['code', 'program', 'function', 'class', 'debug']):
                response = code_llm(query.text)
            else:
                response = general_llm(query.text)
        logger.info("Successfully processed chat request")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}