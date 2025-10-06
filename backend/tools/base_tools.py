from typing import Any, Dict, List
from langchain.tools import BaseTool
import requests
from bs4 import BeautifulSoup
import json
import aiohttp
from datetime import datetime

class WeatherTool(BaseTool):
    name: str = "weather_search"
    description: str = "Search for current weather information using OpenMeteo API"

    async def _arun(self, query: str) -> str:
        # Using free OpenMeteo API
        try:
            # First, get coordinates (you can enhance this with a free geocoding service)
            # For now, using New York as example
            lat, lon = 40.7128, -74.0060
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                async with session.get(url) as response:
                    data = await response.json()
                    weather = data.get('current_weather', {})
                    return f"Current temperature: {weather.get('temperature')}°C, Wind speed: {weather.get('windspeed')} km/h"
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for current information"

    async def _arun(self, query: str) -> str:
        # Using Wikipedia API as a free source of information
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': query,
                    'utf8': 1
                }
                async with session.get('https://en.wikipedia.org/w/api.php', params=params) as response:
                    data = await response.json()
                    results = data.get('query', {}).get('search', [])
                    if results:
                        # Get first result's extract
                        title = results[0]['title']
                        extract_params = {
                            'action': 'query',
                            'format': 'json',
                            'prop': 'extracts',
                            'exintro': True,
                            'explaintext': True,
                            'titles': title
                        }
                        async with session.get('https://en.wikipedia.org/w/api.php', params=extract_params) as extract_response:
                            extract_data = await extract_response.json()
                            pages = extract_data.get('query', {}).get('pages', {})
                            page = next(iter(pages.values()))
                            return page.get('extract', 'No information found')
                    return "No results found"
        except Exception as e:
            return f"Error searching web: {str(e)}"

    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")

class APIDocTool(BaseTool):
    name: str = "api_documentation"
    description: str = "Fetch and parse API documentation from OpenAPI/Swagger specs"

    async def _arun(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse OpenAPI spec
                        info = data.get('info', {})
                        paths = data.get('paths', {})
                        
                        # Create summary
                        summary = [
                            f"API Name: {info.get('title')}",
                            f"Version: {info.get('version')}",
                            f"Description: {info.get('description')}",
                            "\nEndpoints:",
                        ]
                        
                        for path, methods in paths.items():
                            for method, details in methods.items():
                                summary.append(f"\n{method.upper()} {path}")
                                summary.append(f"Description: {details.get('description', 'No description')}")
                                
                        return "\n".join(summary)
                    return f"Error: Could not fetch API documentation (Status: {response.status})"
        except Exception as e:
            return f"Error fetching API documentation: {str(e)}"

    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Useful for performing mathematical calculations"

    def _run(self, query: str) -> str:
        try:
            return str(eval(query))
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

def get_tools() -> List[BaseTool]:
    """Returns a list of available tools."""
    return [
        WeatherTool(),
        WebSearchTool(),
        APIDocTool(),
        CalculatorTool(),
    ]