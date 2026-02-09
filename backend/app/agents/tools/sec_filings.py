"""SEC EDGAR filings search tool."""

import httpx
import structlog
from urllib.parse import quote

from app.agents.tools.base import Tool

logger = structlog.get_logger()

# SEC EDGAR full-text search API
EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_BASE_URL = "https://www.sec.gov"

# User-Agent required by SEC (include contact email)
SEC_USER_AGENT = "ScoutBot/1.0 (contact@aquaregia.life)"


class SECFilingsTool(Tool):
    """Search SEC EDGAR filings for public company information."""
    
    @property
    def name(self) -> str:
        return "sec_filings"
    
    @property
    def description(self) -> str:
        return (
            "Search SEC EDGAR filings for public companies. Returns 10-K (annual reports), "
            "10-Q (quarterly reports), 8-K (current events), and other filings. "
            "Useful for finding financial information, strategic priorities, executive commentary, "
            "and material business events for publicly traded companies."
        )
    
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The company name to search for (e.g., 'Apple Inc', 'Microsoft').",
                },
                "filing_type": {
                    "type": "string",
                    "description": "Optional filing type filter: '10-K', '10-Q', '8-K', or leave empty for all.",
                    "enum": ["10-K", "10-Q", "8-K", ""],
                },
                "keywords": {
                    "type": "string",
                    "description": "Optional keywords to search within filings (e.g., 'cloud migration', 'AI strategy').",
                },
            },
            "required": ["company_name"],
        }
    
    async def execute(
        self,
        company_name: str,
        filing_type: str = "",
        keywords: str = "",
    ) -> dict:
        """
        Search SEC filings for a company.
        
        Returns:
            {
                "company_name": str,
                "filings": [
                    {
                        "filing_type": str,
                        "filed_date": str,
                        "company": str,
                        "description": str,
                        "url": str,
                        "excerpt": str | None,
                    }
                ],
                "total_found": int,
            }
        """
        headers = {
            "User-Agent": SEC_USER_AGENT,
            "Accept": "application/json",
        }
        
        # Build search query
        query_parts = [f'companyName:"{company_name}"']
        
        if filing_type:
            query_parts.append(f'formType:"{filing_type}"')
        
        if keywords:
            query_parts.append(f'"{keywords}"')
        
        query = " AND ".join(query_parts)
        
        params = {
            "q": query,
            "dateRange": "custom",
            "startdt": "2020-01-01",  # Last ~5 years
            "enddt": "2026-12-31",
            "forms": filing_type if filing_type else "-0",  # -0 means all forms
            "from": 0,
            "size": 10,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    EDGAR_SEARCH_URL,
                    headers=headers,
                    params=params,
                    timeout=15.0,
                )
                response.raise_for_status()
                data = response.json()
        
        except httpx.HTTPStatusError as e:
            logger.warning("SEC search failed", status=e.response.status_code)
            return {
                "company_name": company_name,
                "filings": [],
                "total_found": 0,
                "error": f"SEC API returned HTTP {e.response.status_code}",
            }
        except Exception as e:
            logger.error("SEC search error", error=str(e))
            return {
                "company_name": company_name,
                "filings": [],
                "total_found": 0,
                "error": str(e),
            }
        
        # Parse results
        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        
        filings = []
        for hit in hits:
            source = hit.get("_source", {})
            
            # Build filing URL
            accession = source.get("adsh", "").replace("-", "")
            cik = source.get("ciks", [""])[0] if source.get("ciks") else ""
            file_name = source.get("file_name", "")
            
            if accession and cik:
                url = f"{EDGAR_BASE_URL}/Archives/edgar/data/{cik}/{accession}/{file_name}"
            else:
                url = ""
            
            # Extract excerpt if available
            excerpt = None
            highlights = hit.get("highlight", {})
            if highlights:
                # Get first highlight
                for field, excerpts in highlights.items():
                    if excerpts:
                        excerpt = excerpts[0][:500]  # Limit excerpt length
                        break
            
            filings.append({
                "filing_type": source.get("form", ""),
                "filed_date": source.get("file_date", ""),
                "company": source.get("display_names", [company_name])[0],
                "description": source.get("file_description", ""),
                "url": url,
                "excerpt": excerpt,
            })
        
        logger.info(
            "SEC filings search completed",
            company=company_name,
            filing_type=filing_type or "all",
            results=len(filings),
        )
        
        return {
            "company_name": company_name,
            "filings": filings,
            "total_found": total,
        }
