"""
ShortLink API — a modern URL shortening service.

Built with FastAPI and SQLAlchemy, this service provides:
  • URL shortening with cryptographically random short codes
  • Click tracking and analytics
  • Interactive API documentation (Swagger UI / ReDoc)
  • Containerized deployment via Docker
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes.urls import router as urls_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    On startup: create all database tables if they do not exist.
    On shutdown: no explicit cleanup needed (SQLAlchemy handles
    connection pooling closure on process exit).
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ShortLink API",
    description=__doc__,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "MLH Fellowship Application",
        "url": "https://github.com/lumi-19/MLH_repo",
    },
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    """Simple health-check endpoint for monitoring / load balancers."""
    return {"status": "healthy", "service": "shortlink-api"}


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(urls_router, tags=["URL Shortener"])
