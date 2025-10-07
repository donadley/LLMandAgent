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
        # Using free OpenMeteo API and Nominatim for geocoding
        try:
            # First, get coordinates using Nominatim geocoding
            location = query.lower().replace("weather in ", "").replace("what's the weather in ", "").replace("what is the weather in ", "").strip()
            if not location or location == "today" or "current" in location:
                # Default to New York if no location specified
                lat, lon = 40.7128, -74.0060
                location = "New York"
            else:
                # Use Nominatim geocoding
                async with aiohttp.ClientSession() as session:
                    geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
                    headers = {'User-Agent': 'LLMandAgent/1.0'}
                    async with session.get(geocode_url, headers=headers) as geocode_response:
                        geocode_data = await geocode_response.json()
                        if not geocode_data:
                            return f"Could not find location: {location}"
                        lat = float(geocode_data[0]['lat'])
                        lon = float(geocode_data[0]['lon'])
            
            # Get weather data
            async with aiohttp.ClientSession() as session:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
                async with session.get(url) as response:
                    data = await response.json()
                    current = data.get('current', {})
                    
                    # Convert weather code to description
                    weather_codes = {
                        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                        45: "Foggy", 48: "Depositing rime fog",
                        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                        77: "Snow grains", 85: "Snow showers", 86: "Heavy snow showers",
                        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
                    }
                    weather_desc = weather_codes.get(current.get('weather_code'), "Unknown conditions")
                    
                    return (f"Current weather in {location}:\n"
                           f"• Conditions: {weather_desc}\n"
                           f"• Temperature: {current.get('temperature_2m')}°C (Feels like: {current.get('apparent_temperature')}°C)\n"
                           f"• Humidity: {current.get('relative_humidity_2m')}%\n"
                           f"• Wind: {current.get('wind_speed_10m')} km/h from {current.get('wind_direction_10m')}°\n"
                           f"• Precipitation: {current.get('precipitation')} mm")
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Use this tool when you need to search for information about topics, animals, history, or any general knowledge. Input should be a search query."

    async def _arun(self, query: str) -> str:
        # Using Wikipedia API as a free source of information
        try:
            # Add proper user agent and headers for Wikipedia API
            headers = {
                'User-Agent': 'LLMandAgent/1.0 (https://github.com/donadley/LLMandAgent; info@llmandagent.com) Python/3.9',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                # First search for articles
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': str(query),
                    'utf8': '1',  # Changed to string
                    'srlimit': '3'  # Changed to string
                }
                
                async with session.get('https://en.wikipedia.org/w/api.php', params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"Error: Could not search Wikipedia (Status: {response.status}). {error_text}"
                        
                    try:
                        data = await response.json()
                    except Exception as e:
                        return f"Error: Could not parse Wikipedia response. {str(e)}"
                        
                    results = data.get('query', {}).get('search', [])
                    if not results:
                        return "No results found for your query."
                    
                    # Get extracts for top results
                    titles = [result['title'] for result in results[:3]]
                    extract_params = {
                        'action': 'query',
                        'format': 'json',
                        'prop': 'extracts',
                        'exintro': '1',  # Changed to string
                        'explaintext': '1',  # Changed to string
                        'titles': '|'.join(titles)
                    }
                    
                    async with session.get('https://en.wikipedia.org/w/api.php', params=extract_params) as extract_response:
                        if extract_response.status != 200:
                            return f"Error: Could not fetch article details (Status: {extract_response.status})"
                            
                        extract_data = await extract_response.json()
                        pages = extract_data.get('query', {}).get('pages', {})
                        
                        # Combine information from multiple results
                        summaries = []
                        for page in pages.values():
                            title = page.get('title', '')
                            extract = page.get('extract', '')
                            if extract:
                                # Limit extract length and add to summaries
                                summary = f"\n• {title}:\n{extract[:500]}..."
                                summaries.append(summary)
                        
                        if summaries:
                            return "Here's what I found:" + ''.join(summaries)
                        else:
                            return "Found articles but couldn't get detailed information."
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