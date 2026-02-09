"""Web scraping tool using httpx and BeautifulSoup."""

import re
import httpx
import structlog
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.agents.tools.base import Tool

logger = structlog.get_logger()

# Elements to remove from scraped content
REMOVE_TAGS = [
    "script", "style", "nav", "header", "footer", "aside",
    "form", "button", "iframe", "noscript", "svg", "img",
    "video", "audio", "canvas", "map", "figure",
]

# Common ad/tracking class patterns
REMOVE_CLASS_PATTERNS = [
    r"ad[-_]?", r"banner", r"sidebar", r"popup", r"modal",
    r"newsletter", r"subscribe", r"social", r"share", r"comment",
    r"cookie", r"gdpr", r"privacy", r"tracking",
]

MAX_CONTENT_LENGTH = 8000  # Characters


class WebScrapeTool(Tool):
    """Fetch and extract readable content from a web page."""
    
    @property
    def name(self) -> str:
        return "web_scrape"
    
    @property
    def description(self) -> str:
        return (
            "Fetch and extract the main readable content from a specific web page. "
            "Use this after web_search to get detailed information from promising URLs. "
            "Returns the page title, main text content, headings, and meta description."
        )
    
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the page to scrape.",
                },
                "extract_headings": {
                    "type": "boolean",
                    "description": "Whether to extract section headings. Default is true.",
                    "default": True,
                },
            },
            "required": ["url"],
        }
    
    async def execute(self, url: str, extract_headings: bool = True) -> dict:
        """
        Scrape a web page and extract content.
        
        Returns:
            {
                "url": str,
                "title": str,
                "meta_description": str | None,
                "headings": [str] | None,
                "content": str,
                "content_length": int,
                "truncated": bool,
            }
        """
        # Validate URL
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {
                "url": url,
                "error": "Invalid URL scheme. Must be http or https.",
            }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ScoutBot/1.0; +https://aquaregia.life)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return {
                        "url": url,
                        "error": f"Not an HTML page: {content_type}",
                    }
                
                html = response.text
        
        except httpx.TimeoutException:
            return {"url": url, "error": "Request timed out"}
        except httpx.HTTPStatusError as e:
            return {"url": url, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"url": url, "error": str(e)}
        
        # Parse HTML
        soup = BeautifulSoup(html, "lxml")
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        
        # Extract meta description
        meta_desc = None
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_desc = meta_tag.get("content", "").strip()
        
        # Remove unwanted elements
        for tag in REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with ad-related classes
        for pattern in REMOVE_CLASS_PATTERNS:
            regex = re.compile(pattern, re.IGNORECASE)
            for element in soup.find_all(class_=regex):
                element.decompose()
        
        # Extract headings
        headings = None
        if extract_headings:
            headings = []
            for h in soup.find_all(["h1", "h2", "h3"]):
                text = h.get_text(strip=True)
                if text and len(text) < 200:
                    headings.append(text)
            headings = headings[:20]  # Limit to 20 headings
        
        # Extract main content
        # Try to find main content area
        main_content = (
            soup.find("main") or 
            soup.find("article") or 
            soup.find(id=re.compile(r"content|main|article", re.I)) or
            soup.find(class_=re.compile(r"content|main|article", re.I)) or
            soup.body
        )
        
        if main_content:
            # Get text with some structure
            text_parts = []
            for element in main_content.find_all(["p", "li", "td", "th", "div"]):
                text = element.get_text(separator=" ", strip=True)
                if text and len(text) > 20:  # Skip tiny fragments
                    text_parts.append(text)
            
            content = "\n\n".join(text_parts)
        else:
            content = soup.get_text(separator=" ", strip=True)
        
        # Clean up whitespace
        content = re.sub(r"\s+", " ", content).strip()
        
        # Truncate if needed
        truncated = False
        if len(content) > MAX_CONTENT_LENGTH:
            # Try to truncate at sentence boundary
            truncated = True
            content = content[:MAX_CONTENT_LENGTH]
            last_period = content.rfind(".")
            if last_period > MAX_CONTENT_LENGTH * 0.8:
                content = content[:last_period + 1]
        
        logger.info(
            "Web scrape completed",
            url=url,
            content_length=len(content),
            truncated=truncated,
        )
        
        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "headings": headings,
            "content": content,
            "content_length": len(content),
            "truncated": truncated,
        }
