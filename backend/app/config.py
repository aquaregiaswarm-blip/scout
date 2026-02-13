"""Application configuration via Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "Scout"
    environment: str = "development"
    debug: bool = False
    
    # GCP / Vertex AI
    google_cloud_project: str = "prj-cts-lab-vertex-sandbox"
    google_cloud_region: str = "us-east5"  # Claude models available in us-east5
    claude_model: str = "claude-sonnet-4"
    
    # Aliases for compatibility
    @property
    def gcp_project_id(self) -> str:
        return self.google_cloud_project
    
    @property
    def vertex_ai_region(self) -> str:
        return self.google_cloud_region
    
    # Brave Search
    brave_search_api_key: str = ""
    
    # Database
    database_url: str = "postgresql+asyncpg://scout:scout@localhost:5432/scout"
    
    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Agent settings
    max_research_cycles: int = 6
    max_subagents_per_cycle: int = 5
    tool_timeout_seconds: int = 15
    tool_call_budget: int = 10
    
    # SSE
    sse_heartbeat_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
