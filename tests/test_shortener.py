"""
Integration tests for the ShortLink API.

Covers the full request/response cycle including URL creation,
redirects, click tracking, and error handling — all against an
isolated test database.
"""

import pytest
from fastapi import status


class TestShortenURL:
    """Tests for the POST /shorten endpoint."""

    def test_shorten_valid_url(self, client):
        """A valid URL should return 201 with the shortened link metadata."""
        response = client.post("/shorten", json={"original_url": "https://example.com"})
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["original_url"] == "https://example.com/"
        assert len(data["short_code"]) == 6
        assert data["short_url"].endswith(f"/{data['short_code']}")
        assert data["clicks"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_shorten_with_path(self, client):
        """URLs with paths and query parameters should be preserved."""
        url = "https://example.com/blog/post?utm_source=test&ref=mlh"
        response = client.post("/shorten", json={"original_url": url})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["original_url"] == url

    def test_shorten_empty_body_returns_422(self, client):
        """Missing request body should return a validation error."""
        response = client.post("/shorten", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_shorten_invalid_url_returns_422(self, client):
        """Malformed URLs should be rejected by Pydantic validation."""
        response = client.post("/shorten", json={"original_url": "not-a-url"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRedirect:
    """Tests for the GET /{short_code} endpoint."""

    def test_redirect_follows(self, client):
        """Following a valid short code should redirect to the original URL."""
        create_resp = client.post("/shorten", json={"original_url": "https://example.com"})
        short_code = create_resp.json()["short_code"]

        response = client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "https://example.com/"

    def test_redirect_increments_clicks(self, client):
        """Each redirect should increment the click counter by one."""
        create_resp = client.post("/shorten", json={"original_url": "https://example.com"})
        short_code = create_resp.json()["short_code"]

        # Clicks should be 0 initially
        stats = client.get(f"/stats/{short_code}")
        assert stats.json()["clicks"] == 0

        # Follow the redirect
        client.get(f"/{short_code}", follow_redirects=False)

        # Clicks should now be 1
        stats = client.get(f"/stats/{short_code}")
        assert stats.json()["clicks"] == 1

    def test_redirect_nonexistent_code_returns_404(self, client):
        """A short code that does not exist should return 404."""
        response = client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_redirect_stats_does_not_increment(self, client):
        """The /stats endpoint should NOT increment the click counter."""
        create_resp = client.post("/shorten", json={"original_url": "https://example.com"})
        short_code = create_resp.json()["short_code"]

        # Get stats multiple times — clicks should stay at 0
        for _ in range(3):
            stats = client.get(f"/stats/{short_code}")
            assert stats.json()["clicks"] == 0


class TestStats:
    """Tests for the GET /stats/{short_code} endpoint."""

    def test_stats_returns_metadata(self, client):
        """Stats should return full metadata for a valid short code."""
        create_resp = client.post("/shorten", json={"original_url": "https://example.com"})
        data = create_resp.json()

        stats_resp = client.get(f"/stats/{data['short_code']}")
        assert stats_resp.status_code == status.HTTP_200_OK

        stats = stats_resp.json()
        assert stats["original_url"] == data["original_url"]
        assert stats["short_code"] == data["short_code"]
        assert stats["clicks"] == 0

    def test_stats_nonexistent_code_returns_404(self, client):
        """Stats for a non-existent short code should return 404."""
        response = client.get("/stats/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthCheck:
    """Tests for the GET /health endpoint."""

    def test_health_returns_healthy(self, client):
        """The health endpoint should confirm the service is running."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy", "service": "shortlink-api"}


class TestUniqueShortCodes:
    """Verify that generated short codes are unique."""

    def test_multiple_shortenings_produce_different_codes(self, client):
        """Shortening the same URL twice should produce different codes."""
        url = "https://example.com"
        code1 = client.post("/shorten", json={"original_url": url}).json()["short_code"]
        code2 = client.post("/shorten", json={"original_url": url}).json()["short_code"]
        assert code1 != code2