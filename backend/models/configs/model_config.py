from typing import Dict, Any, Optional
from enum import Enum

class ModelType(Enum):
    GENERAL = "general"
    CODE = "code"

class ModelConfig:
    def __init__(
        self,
        name: str,
        model_path: str,
        model_type: ModelType,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context_window: int = 4096
    ):
        self.name = name
        self.model_path = model_path
        self.model_type = model_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window

AVAILABLE_MODELS = {
    ModelType.GENERAL: ModelConfig(
        name="mistral-7b-instruct",
        model_path="./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        model_type=ModelType.GENERAL,
        temperature=0.7,
        max_tokens=2000,
    ),
    ModelType.CODE: ModelConfig(
        name="codellama-7b-instruct",
        model_path="./models/codellama-7b-instruct.Q5_K_M.gguf",
        model_type=ModelType.CODE,
        temperature=0.2,
        max_tokens=4000,
    )
}