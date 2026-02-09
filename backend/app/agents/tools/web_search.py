"""Web search tool using Brave Search API."""

import httpx
import structlog

from app.agents.tools.base import Tool
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


class WebSearchTool(Tool):
    """Search the web using Brave Search API."""
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return (
            "Search the web for information about companies, people, technologies, "
            "and topics. Returns a list of relevant web pages with titles, URLs, "
            "and descriptions. Use this to discover relevant sources before scraping."
        )
    
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and include company names, technologies, or topics.",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (1-20). Default is 10.",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["query"],
        }
    
    async def execute(self, query: str, count: int = 10) -> dict:
        """
        Execute a web search.
        
        Returns:
            {
                "query": str,
                "results": [
                    {
                        "title": str,
                        "url": str,
                        "description": str,
                        "age": str | None,
                    }
                ],
                "total_results": int,
            }
        """
        if not settings.brave_search_api_key:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": "Brave Search API key not configured",
            }
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.brave_search_api_key,
        }
        
        params = {
            "q": query,
            "count": min(count, 20),
            "text_decorations": False,
            "search_lang": "en",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BRAVE_SEARCH_URL,
                headers=headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse results
        web_results = data.get("web", {}).get("results", [])
        
        results = []
        for item in web_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "age": item.get("age"),
            })
        
        logger.info(
            "Web search completed",
            query=query,
            result_count=len(results),
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
        }
