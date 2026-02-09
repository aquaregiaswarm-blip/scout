"""Job postings search tool using Brave Search + scraping."""

import re
import httpx
import structlog
from bs4 import BeautifulSoup

from app.agents.tools.base import Tool
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# Common technology keywords to extract
TECH_KEYWORDS = [
    "aws", "azure", "gcp", "google cloud", "kubernetes", "docker",
    "python", "java", "javascript", "typescript", "react", "angular",
    "sql", "postgresql", "mongodb", "redis", "elasticsearch",
    "terraform", "ansible", "jenkins", "github", "gitlab",
    "salesforce", "servicenow", "sap", "oracle", "workday",
    "machine learning", "ai", "data science", "analytics",
    "security", "devops", "sre", "cloud", "microservices",
    "agile", "scrum", "jira", "confluence",
]


class JobPostingsTool(Tool):
    """Search for job postings to infer technology stack and priorities."""
    
    @property
    def name(self) -> str:
        return "job_postings"
    
    @property
    def description(self) -> str:
        return (
            "Search for job postings from a company to infer their technology stack, "
            "team structure, and strategic priorities. Job postings reveal what technologies "
            "they use, what skills they're hiring for, and what initiatives they're investing in."
        )
    
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The company name to search jobs for.",
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional keywords to filter jobs (e.g., ['cloud', 'security', 'data']).",
                },
            },
            "required": ["company_name"],
        }
    
    async def execute(
        self,
        company_name: str,
        keywords: list[str] | None = None,
    ) -> dict:
        """
        Search for job postings from a company.
        
        Returns:
            {
                "company_name": str,
                "jobs": [
                    {
                        "title": str,
                        "url": str,
                        "source": str,
                        "description_excerpt": str,
                        "technologies_mentioned": [str],
                        "seniority": str | None,
                    }
                ],
                "technology_signals": [str],
                "total_found": int,
            }
        """
        if not settings.brave_search_api_key:
            return {
                "company_name": company_name,
                "jobs": [],
                "technology_signals": [],
                "total_found": 0,
                "error": "Brave Search API key not configured",
            }
        
        # Build search query
        query_parts = [f'"{company_name}"', "careers OR jobs OR hiring"]
        if keywords:
            query_parts.append(" OR ".join(keywords))
        
        query = " ".join(query_parts)
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.brave_search_api_key,
        }
        
        params = {
            "q": query,
            "count": 15,
            "text_decorations": False,
            "search_lang": "en",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    BRAVE_SEARCH_URL,
                    headers=headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
        
        except Exception as e:
            return {
                "company_name": company_name,
                "jobs": [],
                "technology_signals": [],
                "total_found": 0,
                "error": str(e),
            }
        
        # Parse search results
        web_results = data.get("web", {}).get("results", [])
        
        jobs = []
        all_technologies = set()
        
        for item in web_results:
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            
            # Skip if doesn't look like a job posting
            if not self._looks_like_job(title, url):
                continue
            
            # Extract technologies mentioned
            text_to_scan = f"{title} {description}".lower()
            technologies = self._extract_technologies(text_to_scan)
            all_technologies.update(technologies)
            
            # Infer seniority
            seniority = self._infer_seniority(title)
            
            jobs.append({
                "title": title,
                "url": url,
                "source": self._get_domain(url),
                "description_excerpt": description[:300] if description else "",
                "technologies_mentioned": list(technologies),
                "seniority": seniority,
            })
        
        # Limit to top 10 most relevant
        jobs = jobs[:10]
        
        logger.info(
            "Job postings search completed",
            company=company_name,
            jobs_found=len(jobs),
            technologies=list(all_technologies),
        )
        
        return {
            "company_name": company_name,
            "jobs": jobs,
            "technology_signals": sorted(list(all_technologies)),
            "total_found": len(jobs),
        }
    
    def _looks_like_job(self, title: str, url: str) -> bool:
        """Check if a result looks like a job posting."""
        job_indicators = [
            "career", "job", "position", "hiring", "apply",
            "engineer", "manager", "director", "analyst", "developer",
            "specialist", "coordinator", "lead", "architect",
        ]
        title_lower = title.lower()
        url_lower = url.lower()
        
        return any(ind in title_lower or ind in url_lower for ind in job_indicators)
    
    def _extract_technologies(self, text: str) -> set[str]:
        """Extract technology keywords from text."""
        found = set()
        for tech in TECH_KEYWORDS:
            if tech in text:
                found.add(tech)
        return found
    
    def _infer_seniority(self, title: str) -> str | None:
        """Infer seniority level from job title."""
        title_lower = title.lower()
        
        if any(x in title_lower for x in ["senior", "sr.", "sr ", "lead", "principal", "staff"]):
            return "senior"
        elif any(x in title_lower for x in ["director", "head of", "vp", "vice president"]):
            return "director"
        elif any(x in title_lower for x in ["manager", "mgr"]):
            return "manager"
        elif any(x in title_lower for x in ["junior", "jr.", "jr ", "entry", "associate"]):
            return "junior"
        elif any(x in title_lower for x in ["intern", "internship"]):
            return "intern"
        
        return "mid-level"
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
