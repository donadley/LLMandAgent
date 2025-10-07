from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
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
    use_agent: Optional[bool] = None  # Make it optional since we'll determine it automatically

async def classify_query(text: str) -> Dict[str, Any]:
    """Classify the query to determine the best processing method."""
    classification_prompt = f"""Analyze the following query and classify it into one of these categories:
    1. CODE - for questions about programming, debugging, or code explanation
    2. TOOL - for questions requiring external tools (weather, calculations, web search, or any real-time data)
    3. GENERAL - for general knowledge or conversation
    
    Respond in JSON format only with two fields:
    - category: CODE, TOOL, or GENERAL
    - reason: brief explanation of the classification
    
    Query: {text}
    """
    
    try:
        response = general_llm(classification_prompt)
        # Clean up the response to ensure valid JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:-3]  # Remove ```json and ```
        elif response.startswith("{\n"):
            response = response  # Keep as is
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error classifying query: {str(e)}")
        return {"category": "GENERAL", "reason": "Classification failed, defaulting to general"}

@app.post("/api/chat")
async def chat(query: Query):
    logger.info(f"Received chat request: {query.text[:100]}...")
    try:
        # Classify the query
        classification = await classify_query(query.text)
        logger.info(f"Query classified as: {classification['category']} - {classification['reason']}")
        
        # Override classification if use_agent is explicitly set
        if query.use_agent is not None:
            if query.use_agent:
                response = await agent_manager.process_message(query.text)
            else:
                response = general_llm(query.text)
        else:
            # Route based on classification
            if classification['category'] == 'CODE':
                logger.info("Using code LLM for processing")
                response = code_llm(query.text)
            elif classification['category'] == 'TOOL':
                logger.info("Using agent for tool-based processing")
                response = await agent_manager.process_message(query.text)
            else:  # GENERAL
                logger.info("Using general LLM for processing")
                response = general_llm(query.text)
                
        logger.info("Successfully processed chat request")
        return {
            "response": response,
            "classification": classification  # Include classification in response for transparency
        }
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}