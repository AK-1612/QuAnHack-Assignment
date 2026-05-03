"""
FastAPI application initialization with core middleware and routing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from src.config import settings
from src.api.v1.endpoints import webhooks, leads
from src.database.session import init_db, close_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("🚀 Starting Travel Itinerary Assistant...")
    
    # Create tables if they don't exist
    from src.models.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    await init_db()
    yield
    await close_db()
    logger.info("🛑 Shutting down Travel Itinerary Assistant...")

def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    # API v1 routes
    app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
    app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
