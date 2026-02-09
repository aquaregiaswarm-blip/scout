"""News search tool using Brave Search API."""

import httpx
import structlog

from app.agents.tools.base import Tool
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

BRAVE_NEWS_URL = "https://api.search.brave.com/res/v1/news/search"


class NewsSearchTool(Tool):
    """Search for recent news articles using Brave News API."""
    
    @property
    def name(self) -> str:
        return "news_search"
    
    @property
    def description(self) -> str:
        return (
            "Search for recent news articles about a company or topic. "
            "Returns recent press releases, news coverage, and announcements. "
            "Useful for finding current events, executive quotes, and recent developments."
        )
    
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Include company name and topic for best results.",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (1-20). Default is 10.",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 20,
                },
                "freshness": {
                    "type": "string",
                    "description": "How recent the news should be. Options: 'past_day', 'past_week', 'past_month'.",
                    "enum": ["past_day", "past_week", "past_month", ""],
                },
            },
            "required": ["query"],
        }
    
    async def execute(
        self,
        query: str,
        count: int = 10,
        freshness: str = "",
    ) -> dict:
        """
        Search for news articles.
        
        Returns:
            {
                "query": str,
                "results": [
                    {
                        "title": str,
                        "url": str,
                        "source": str,
                        "published_date": str,
                        "description": str,
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
        
        # Map freshness to Brave API format
        if freshness == "past_day":
            params["freshness"] = "pd"
        elif freshness == "past_week":
            params["freshness"] = "pw"
        elif freshness == "past_month":
            params["freshness"] = "pm"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    BRAVE_NEWS_URL,
                    headers=headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
        
        except httpx.HTTPStatusError as e:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": f"Brave API returned HTTP {e.response.status_code}",
            }
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": str(e),
            }
        
        # Parse results
        news_results = data.get("results", [])
        
        results = []
        for item in news_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("meta_url", {}).get("hostname", ""),
                "published_date": item.get("age", ""),
                "description": item.get("description", ""),
            })
        
        logger.info(
            "News search completed",
            query=query,
            freshness=freshness or "any",
            result_count=len(results),
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
        }
