"""
Pydantic schemas for request validation and response serialization.

These schemas enforce the API contract — every route declares
exactly what data it expects and what it returns.
"""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class URLShortenRequest(BaseModel):
    """
    Request body for creating a shortened URL.
    Uses Pydantic's HttpUrl type to enforce valid URLs at the API boundary.
    """
    original_url: HttpUrl = Field(
        ...,
        description="The original long URL to shorten",
        examples=["https://www.example.com/very/long/path?query=param"],
    )


class URLResponse(BaseModel):
    """Public response returned after creating or fetching a short URL."""

    id: int
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}


class URLStatsResponse(BaseModel):
    """Detailed statistics for a shortened URL."""

    id: int
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str


class HealthResponse(BaseModel):
    """Response for the health-check endpoint."""

    status: str
    service: str
