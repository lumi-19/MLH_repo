"""
API route handlers for URL shortening operations.

Every endpoint is deliberately kept thin — validation is handled
by Pydantic schemas, persistence by the CRUD layer, and utilities
by helper functions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import create_short_url, get_by_short_code, increment_clicks
from app.database import get_db
from app.schemas import URLResponse, URLShortenRequest, URLStatsResponse
from app.utils import generate_short_code

router = APIRouter()


def _build_short_url(short_code: str) -> str:
    """Build the fully qualified short URL for a given code."""
    base = settings.base_url.rstrip("/")
    return f"{base}/{short_code}"


@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a shortened URL",
    description="Takes a long URL and returns a shortened version with a unique code.",
)
def shorten_url(
    request: URLShortenRequest,
    db: Session = Depends(get_db),
):
    """
    Create a shortened URL.

    Generates a cryptographically random short code, persists the
    mapping to the database, and returns the full shortened URL
    along with metadata.
    """
    original_url = str(request.original_url)

    # Generate a unique short code (collisions are astronomically
    # unlikely with 62^6 combinations, but we loop just in case).
    short_code = generate_short_code(settings.short_code_length)
    while get_by_short_code(db, short_code):
        short_code = generate_short_code(settings.short_code_length)

    entry = create_short_url(db, original_url, short_code)

    return URLResponse(
        id=entry.id,
        original_url=entry.original_url,
        short_code=entry.short_code,
        short_url=_build_short_url(entry.short_code),
        clicks=entry.clicks,
        created_at=entry.created_at,
    )


@router.get(
    "/{short_code}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to the original URL",
    description="Follow a short code to its destination URL via an HTTP 307 redirect.",
    responses={
        307: {"description": "Temporary redirect to the original URL"},
        404: {"description": "Short code not found"},
    },
)
def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    Redirect a visitor to the original URL.

    Increments the click counter and returns an HTTP 307
    (Temporary Redirect) preserving the HTTP method for
    compatibility.
    """
    entry = get_by_short_code(db, short_code)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No URL found for short code '{short_code}'.",
        )

    increment_clicks(db, entry)
    return RedirectResponse(url=entry.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
    summary="Get statistics for a short URL",
    description="Returns metadata and click count for a given short code without redirecting.",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        404: {"description": "Short code not found"},
    },
)
def get_stats(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve usage statistics for a shortened URL.

    Unlike the redirect endpoint, this does **not** increment
    the click counter — it simply returns the current state.
    """
    entry = get_by_short_code(db, short_code)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No URL found for short code '{short_code}'.",
        )

    return URLStatsResponse(
        id=entry.id,
        original_url=entry.original_url,
        short_code=entry.short_code,
        short_url=_build_short_url(entry.short_code),
        clicks=entry.clicks,
        created_at=entry.created_at,
    )
