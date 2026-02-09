"""FastAPI application entry point."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import init_db, close_db

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Scout", environment=settings.environment)
    await init_db()
    yield
    await close_db()
    logger.info("Scout shutdown complete")


app = FastAPI(
    title="Scout API",
    description="Agentic Sales Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://scout.aquaregia.life",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/api/v1/health/ready")
async def readiness_check():
    """Readiness check - verifies dependencies."""
    # TODO: Check database connection, Vertex AI access
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "vertex_ai": "ok",
        }
    }


# Import and include routers
# from app.routers import research, companies, portfolio, auth
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(research.router, prefix="/api/v1/research", tags=["research"])
# app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
# app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
