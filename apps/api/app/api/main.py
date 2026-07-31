"""
Eli Claw API - Main Application Entry Point

FastAPI application with all routes, middleware, and lifecycle events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import health, projects, domains, crawl, audit, keywords, entities, indexing, citations, recommendations, reports
from app.api import media  # AI Studio - Generative Media Engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    yield
    # Shutdown
    await close_db()
    print("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Eli Claw - AI Search Intelligence SaaS Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["Projects"])
    app.include_router(domains.router, prefix=f"{settings.API_V1_PREFIX}/domains", tags=["Domains"])
    app.include_router(crawl.router, prefix=f"{settings.API_V1_PREFIX}/crawl", tags=["Crawl"])
    app.include_router(audit.router, prefix=f"{settings.API_V1_PREFIX}/audit", tags=["Audit"])
    app.include_router(keywords.router, prefix=f"{settings.API_V1_PREFIX}/keywords", tags=["Keywords"])
    app.include_router(entities.router, prefix=f"{settings.API_V1_PREFIX}/entities", tags=["Entities"])
    app.include_router(indexing.router, prefix=f"{settings.API_V1_PREFIX}/indexing", tags=["Indexing"])
    app.include_router(citations.router, prefix=f"{settings.API_V1_PREFIX}/citations", tags=["Citations"])
    app.include_router(recommendations.router, prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["Recommendations"])
    app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
    
    # AI Studio - Generative Media Engine
    app.include_router(media.router)
    
    return app


# Create app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
