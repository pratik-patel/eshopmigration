"""
FastAPI application entry point.

Initializes and configures the application with:
- CORS middleware
- Router registration
- Error handlers
- Structured logging
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.catalog.router import router as catalog_router
from app.catalog.lookup_router import router as lookup_router
from app.images.router import router as images_router

# Initialize structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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
    """Application lifespan events."""
    # Startup
    logger.info(
        "app.startup",
        app_name=settings.app_name,
        debug=settings.debug,
        db_url=settings.db_url,
    )
    yield
    # Shutdown
    logger.info("app.shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="""
    eShop Catalog Management API - FastAPI Backend

    Provides CRUD operations for catalog items with:
    - Pagination support (default 10 items per page)
    - Image upload and storage
    - Brand and type lookups
    - Full validation and error handling

    **Migration Status:** Like-to-like migration from ASP.NET WebForms
    """,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(
        "app.unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.debug else None,
            }
        },
    )


# Register routers
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(lookup_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
        "message": "eShop Catalog Management API is running",
    }


@app.get("/api/health", tags=["health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
