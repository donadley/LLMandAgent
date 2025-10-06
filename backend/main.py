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
    try:
        if query.use_agent:
            # Use agent for complex queries
            response = await agent_manager.process_message(query.text)
        else:
            # Direct LLM response for simple queries
            response = llm(query.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}