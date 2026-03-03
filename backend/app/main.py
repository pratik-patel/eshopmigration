"""
FastAPI application entry point for eShop Catalog API.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import structlog
import traceback

from app.config import get_settings
from app.core.logging import configure_logging
from app.core.exceptions import NotFoundException

# Import routers
from app.catalog.router import router as catalog_router

# Configure structured logging
configure_logging()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="eShop Catalog API",
    description="Backend API for eShop catalog management (migrated from ASP.NET WebForms)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# Exception handlers
@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Handle NotFoundException."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        "api.unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__,
        },
    )

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for product images
# app.mount("/pics", StaticFiles(directory="static/pics"), name="pics")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "eshop-catalog-api",
        "version": "1.0.0",
    }


# Include routers
app.include_router(catalog_router, prefix="/api/catalog", tags=["catalog"])


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    from app.core.db import init_db
    from app.core.seed import seed_database
    from app.dependencies import get_db_session

    logger.info(
        "eshop.startup",
        service="eshop-catalog-api",
        environment=settings.environment,
        use_mock_adapters=settings.use_mock_adapters,
    )

    # Initialize database tables (in real mode only)
    if not settings.use_mock_adapters:
        logger.info("eshop.startup.init_db")
        await init_db()

        # Seed database with initial data
        async for session in get_db_session():
            await seed_database(session)
            break  # Only need one session


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("eshop.shutdown", service="eshop-catalog-api")
