"""Tests for research tools."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.tools.base import Tool, ToolRegistry, run_tool, create_default_registry
from app.agents.tools.web_search import WebSearchTool
from app.agents.tools.web_scrape import WebScrapeTool
from app.agents.tools.sec_filings import SECFilingsTool
from app.agents.tools.news_search import NewsSearchTool
from app.agents.tools.job_postings import JobPostingsTool


class TestToolRegistry:
    """Tests for ToolRegistry."""
    
    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        registry = ToolRegistry()
        tool = WebSearchTool()
        
        registry.register(tool)
        
        assert registry.get("web_search") is tool
        assert registry.get("unknown") is None
    
    def test_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        registry.register(WebScrapeTool())
        
        tools = registry.list_tools()
        
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"web_search", "web_scrape"}
    
    def test_to_anthropic_tools(self):
        """Test converting to Anthropic tool format."""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        
        tools = registry.to_anthropic_tools()
        
        assert len(tools) == 1
        assert tools[0]["name"] == "web_search"
        assert "description" in tools[0]
        assert "input_schema" in tools[0]
    
    def test_create_default_registry(self):
        """Test creating registry with all default tools."""
        registry = create_default_registry()
        
        assert registry.get("web_search") is not None
        assert registry.get("web_scrape") is not None
        assert registry.get("sec_filings") is not None
        assert registry.get("news_search") is not None
        assert registry.get("job_postings") is not None


class TestRunTool:
    """Tests for run_tool function."""
    
    @pytest.mark.asyncio
    async def test_run_tool_success(self):
        """Test successful tool execution."""
        registry = ToolRegistry()
        
        # Create a mock tool
        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "test_tool"
        mock_tool.execute = AsyncMock(return_value={"data": "test"})
        
        registry.register(mock_tool)
        
        result = await run_tool(registry, "test_tool", {"arg": "value"})
        
        assert "result" in result
        assert result["result"]["data"] == "test"
    
    @pytest.mark.asyncio
    async def test_run_tool_unknown(self):
        """Test running an unknown tool."""
        registry = ToolRegistry()
        
        result = await run_tool(registry, "unknown_tool", {})
        
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_tool_timeout(self):
        """Test tool timeout handling."""
        import asyncio
        
        registry = ToolRegistry()
        
        async def slow_execute(**kwargs):
            await asyncio.sleep(10)
            return {}
        
        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "slow_tool"
        mock_tool.execute = slow_execute
        
        registry.register(mock_tool)
        
        result = await run_tool(registry, "slow_tool", {}, timeout=0.1)
        
        assert "error" in result
        assert "timed out" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_tool_exception(self):
        """Test tool exception handling."""
        registry = ToolRegistry()
        
        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "failing_tool"
        mock_tool.execute = AsyncMock(side_effect=ValueError("Test error"))
        
        registry.register(mock_tool)
        
        result = await run_tool(registry, "failing_tool", {})
        
        assert "error" in result
        assert "Test error" in result["error"]


class TestWebSearchTool:
    """Tests for WebSearchTool."""
    
    def test_tool_properties(self):
        """Test tool has required properties."""
        tool = WebSearchTool()
        
        assert tool.name == "web_search"
        assert "search" in tool.description.lower()
        assert tool.schema["type"] == "object"
        assert "query" in tool.schema["properties"]
    
    @pytest.mark.asyncio
    async def test_execute_no_api_key(self):
        """Test execution fails gracefully without API key."""
        tool = WebSearchTool()
        
        with patch("app.agents.tools.web_search.settings") as mock_settings:
            mock_settings.brave_search_api_key = ""
            
            result = await tool.execute(query="test")
            
            assert "error" in result
            assert result["results"] == []
    
    @pytest.mark.asyncio
    async def test_execute_with_mock_response(self):
        """Test execution with mocked API response."""
        tool = WebSearchTool()
        
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "Test Result",
                        "url": "https://example.com",
                        "description": "A test description",
                        "age": "2 days ago",
                    }
                ]
            }
        }
        
        with patch("app.agents.tools.web_search.settings") as mock_settings:
            mock_settings.brave_search_api_key = "test-key"
            
            with patch("httpx.AsyncClient") as mock_client:
                mock_get = AsyncMock()
                mock_get.return_value.raise_for_status = MagicMock()
                mock_get.return_value.json = MagicMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.get = mock_get
                
                result = await tool.execute(query="test company")
                
                assert len(result["results"]) == 1
                assert result["results"][0]["title"] == "Test Result"


class TestWebScrapeTool:
    """Tests for WebScrapeTool."""
    
    def test_tool_properties(self):
        """Test tool has required properties."""
        tool = WebScrapeTool()
        
        assert tool.name == "web_scrape"
        assert "url" in tool.schema["properties"]
    
    @pytest.mark.asyncio
    async def test_execute_invalid_url(self):
        """Test handling of invalid URL."""
        tool = WebScrapeTool()
        
        result = await tool.execute(url="ftp://invalid.com")
        
        assert "error" in result
        assert "Invalid URL" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_with_mock_html(self):
        """Test execution with mocked HTML response."""
        tool = WebScrapeTool()
        
        mock_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is the main content of the page with some useful information.</p>
            </body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = mock_html
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            result = await tool.execute(url="https://example.com/page")
            
            assert result["title"] == "Test Page"
            assert "content" in result
            assert "Main Heading" in str(result.get("headings", []))


class TestSECFilingsTool:
    """Tests for SECFilingsTool."""
    
    def test_tool_properties(self):
        """Test tool has required properties."""
        tool = SECFilingsTool()
        
        assert tool.name == "sec_filings"
        assert "company_name" in tool.schema["properties"]
    
    @pytest.mark.asyncio
    async def test_execute_with_mock_response(self):
        """Test execution with mocked SEC response."""
        tool = SECFilingsTool()
        
        mock_response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "form": "10-K",
                            "file_date": "2024-01-15",
                            "display_names": ["Apple Inc"],
                            "file_description": "Annual Report",
                            "adsh": "0000320193-24-000001",
                            "ciks": ["320193"],
                            "file_name": "aapl-20231231.htm",
                        }
                    }
                ]
            }
        }
        
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_resp)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            result = await tool.execute(company_name="Apple Inc")
            
            assert len(result["filings"]) == 1
            assert result["filings"][0]["filing_type"] == "10-K"


class TestNewsSearchTool:
    """Tests for NewsSearchTool."""
    
    def test_tool_properties(self):
        """Test tool has required properties."""
        tool = NewsSearchTool()
        
        assert tool.name == "news_search"
        assert "query" in tool.schema["properties"]
        assert "freshness" in tool.schema["properties"]


class TestJobPostingsTool:
    """Tests for JobPostingsTool."""
    
    def test_tool_properties(self):
        """Test tool has required properties."""
        tool = JobPostingsTool()
        
        assert tool.name == "job_postings"
        assert "company_name" in tool.schema["properties"]
    
    def test_infer_seniority(self):
        """Test seniority inference from job titles."""
        tool = JobPostingsTool()
        
        assert tool._infer_seniority("Senior Software Engineer") == "senior"
        assert tool._infer_seniority("Director of Engineering") == "director"
        assert tool._infer_seniority("Engineering Manager") == "manager"
        assert tool._infer_seniority("Junior Developer") == "junior"
        assert tool._infer_seniority("Software Engineer") == "mid-level"
    
    def test_extract_technologies(self):
        """Test technology extraction from text."""
        tool = JobPostingsTool()
        
        text = "experience with aws and kubernetes, python preferred"
        techs = tool._extract_technologies(text)
        
        assert "aws" in techs
        assert "kubernetes" in techs
        assert "python" in techs
