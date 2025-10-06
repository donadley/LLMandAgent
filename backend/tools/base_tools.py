from typing import Any, Dict, List
from langchain.agents import Tool
from langchain.tools import BaseTool

class SearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information"

    def _run(self, query: str) -> str:
        # Placeholder for actual web search implementation
        return f"Searched for: {query}"

    def _arun(self, query: str) -> str:
        # Async implementation
        raise NotImplementedError("async not implemented")

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Useful for performing mathematical calculations"

    def _run(self, query: str) -> str:
        try:
            return str(eval(query))
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    def _arun(self, query: str) -> str:
        raise NotImplementedError("async not implemented")

def get_tools() -> List[Tool]:
    """Returns a list of available tools."""
    return [
        SearchTool(),
        CalculatorTool(),
    ]