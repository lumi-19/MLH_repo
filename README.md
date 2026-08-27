# ShortLink API 🚀

[![CI — Test & Lint](https://github.com/lumi-19/MLH_repo/actions/workflows/ci.yml/badge.svg)](https://github.com/lumi-19/MLH_repo/actions/workflows/ci.yml)

A modern, production-ready **URL shortening service** built with **FastAPI** and **SQLAlchemy**. This project demonstrates clean architecture, comprehensive testing, DevOps best practices, and real-world deployability — exactly the kind of code the MLH Fellowship looks for.

---

## Table of Contents

- [Why This Project?](#why-this-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [API Reference](#api-reference)
- [Testing](#testing)
- [CI / CD](#ci--cd)
- [Project Structure](#project-structure)
- [What This Demonstrates](#what-this-demonstrates)
- [License](#license)

---

## Why This Project?

URL shortening solves a **real problem** — turning long, unwieldy links into clean, shareable short codes. Services like bit.ly and TinyURL process billions of redirects daily.

This implementation is purposely **small enough to have a conversation about** in a 45-minute technical interview, but **substantial enough to demonstrate**:

- **Clean architecture** — separation of concerns across layers
- **Production readiness** — Docker, health checks, environment configuration
- **Testing discipline** — isolated test database, comprehensive test suite
- **Modern Python** — type hints, async, Pydantic validation, SQLAlchemy 2.0
- **DevOps / SRE skills** — containerization, CI pipeline, monitoring endpoints
- **Documentation** — auto-generated OpenAPI (Swagger/ReDoc) + this README

---

## Features

| Feature | Details |
|---------|---------|
| ✂️ **URL Shortening** | Cryptographically random 6-character short codes (62⁶ ≈ 56 billion combinations) |
| 🔄 **Redirects** | HTTP 307 Temporary Redirect — preserves method semantics |
| 📊 **Click Tracking** | Automatic counter increments on every redirect |
| 🛡️ **Input Validation** | Pydantic schemas enforce valid URLs at the API boundary |
| 📖 **Interactive Docs** | Swagger UI at `/docs` and ReDoc at `/redoc` |
| 🐳 **Dockerized** | Multi-stage Dockerfile + docker-compose for one-command startup |
| 🧪 **Tested** | 12 integration tests covering happy paths, edge cases, and error handling |
| 🔄 **CI Pipeline** | GitHub Actions — lint + test across Python 3.11 and 3.12 |
| 🏥 **Health Check** | `/health` endpoint for load balancers and monitoring |

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Language** | Python 3.12 | Modern type hints, pattern matching, performance |
| **Framework** | FastAPI | Async-native, auto-docs, Pydantic integration |
| **ORM** | SQLAlchemy 2.0 | Industry-standard Python ORM with modern 2.0 style |
| **Validation** | Pydantic v2 | Runtime type checking, JSON Schema generation |
| **Config** | pydantic-settings | Type-safe environment variable loading |
| **Testing** | pytest + httpx | FastAPI TestClient for async integration tests |
| **Container** | Docker multi-stage | Minimal runtime image, security best practices |
| **CI** | GitHub Actions | Matrix testing across Python versions, coverage enforcement |

---

## Architecture

The application follows a **layered architecture** with clear separation of concerns:

```
HTTP Request
    │
    ▼
┌──────────────────────┐
│   FastAPI Routes     │  ← request/response handling, status codes
│   (routes/urls.py)   │
├──────────────────────┤
│   Pydantic Schemas   │  ← input validation, response serialization
│   (schemas.py)       │
├──────────────────────┤
│   CRUD Layer         │  ← database operations, business logic
│   (crud.py)          │
├──────────────────────┤
│   SQLAlchemy Models  │  ← ORM mappings, table definitions
│   (models.py)        │
├──────────────────────┤
│   Database Engine    │  ← connection pooling, session management
│   (database.py)      │
└──────────────────────┘
```

**Key design decisions:**

- **Thin routes, fat services** — route handlers delegate to CRUD functions and never touch SQL directly.
- **Dependency injection** — FastAPI's `Depends(get_db)` provides clean session lifecycle without global state.
- **Configuration at the edge** — all environment-sensitive values flow through `Settings`, making the app portable across environments.
- **Data validation at the boundary** — Pydantic schemas reject invalid input before it reaches business logic.

---

## Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/lumi-19/MLH_repo.git
cd MLH_repo

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional — defaults work out of the box)
cp .env.example .env

# 5. Run the server
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**. Open **http://localhost:8000/docs** for the interactive Swagger UI.

### Docker

```bash
# Start the service with one command
docker compose up --build

# The API is now at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

The container includes a health check — Docker will automatically restart it on failure.

---

## API Reference

### `POST /shorten` — Create a Short URL

```
POST /shorten
Content-Type: application/json

{
  "original_url": "https://www.example.com/very/long/path?query=param"
}
```

**Response** `201 Created`

```json
{
  "id": 1,
  "original_url": "https://www.example.com/very/long/path?query=param",
  "short_code": "aB3xK9",
  "short_url": "http://localhost:8000/aB3xK9",
  "clicks": 0,
  "created_at": "2026-08-27T12:00:00Z"
}
```

### `GET /{short_code}` — Follow a Short URL

```
GET /aB3xK9
```

**Response** — `307 Temporary Redirect` to the original URL.
Calls to this endpoint increment the click counter.

### `GET /stats/{short_code}` — Get URL Statistics

```
GET /stats/aB3xK9
```

**Response** `200 OK`

```json
{
  "id": 1,
  "original_url": "https://www.example.com/very/long/path?query=param",
  "short_code": "aB3xK9",
  "short_url": "http://localhost:8000/aB3xK9",
  "clicks": 5,
  "created_at": "2026-08-27T12:00:00Z"
}
```

This endpoint does **not** increment the click counter.

### `GET /health` — Health Check

```
GET /health
```

**Response** `200 OK`

```json
{
  "status": "healthy",
  "service": "shortlink-api"
}
```

---

## Testing

The test suite uses an **isolated SQLite database** that is created per-test-function and destroyed afterward, ensuring zero interference between tests.

```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test class
pytest tests/test_shortener.py -v -k "TestShortenURL"
```

**Current test coverage** covers:

| Category | Tests |
|----------|-------|
| ✅ URL creation | Valid URLs, empty body, malformed input |
| ✅ Redirects | Following redirects, non-existent codes |
| ✅ Click tracking | Increment on redirect, no increment on stats |
| ✅ Statistics | Metadata retrieval, missing code handling |
| ✅ Health check | Correct status response |
| ✅ Uniqueness | Multiple shortenings produce different codes |

---

## CI / CD

The project includes a **GitHub Actions CI pipeline** (`.github/workflows/ci.yml`) that runs on every push and pull request:

1. **Checkout** the repository
2. **Set up Python** (matrix across 3.11 and 3.12)
3. **Install dependencies** (with pip caching for speed)
4. **Lint** with flake8 (max complexity 10, line length 100)
5. **Test** with pytest (coverage threshold ≥ 80%)
6. **Upload coverage report** as a build artifact

![CI Pipeline](https://github.com/lumi-19/MLH_repo/actions/workflows/ci.yml/badge.svg)

---

## Project Structure

```
MLH_repo/
├── app/                     # Application package
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point, lifespan, middleware
│   ├── config.py            # Type-safe environment configuration
│   ├── database.py          # Database engine, session, declarative base
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # Database CRUD operations
│   ├── utils.py             # Helper utilities (short code generation)
│   └── routes/              # API route handlers
│       ├── __init__.py
│       └── urls.py          # URL shortening endpoints
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Fixtures & test configuration
│   └── test_shortener.py    # Integration tests
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # One-command deployment
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── .gitignore
├── .github/workflows/
│   └── ci.yml               # CI pipeline
└── README.md                # This file
```

**File count:** 14 source files across multiple packages — substantial enough for a meaningful code review, compact enough to discuss in one interview.

---

## What This Demonstrates

This project was built as a code sample for the **[MLH Fellowship](https://mlh.io/fellowship)** application. Here is how it maps to what MLH looks for:

| MLH Requirement | How This Project Meets It |
|----------------|---------------------------|
| **Representative** | Clean, well-structured Python with modern patterns, type hints, and testing — reflects how I actually write code. |
| **Existing sample** | Built specifically for this application, solving a real problem. |
| **Public on GitHub** | Hosted at [lumi-19/MLH_repo](https://github.com/lumi-19/MLH_repo). |
| **Multiple files** | 14 files across a well-organized package structure.|
| **Not too large** | Concise enough to understand in minutes, but with real substance.|
| **Real problem** | URL shortening is a widely-used service with real-world demands.|
| **No Jupyter notebooks** | Deployable web application with Docker and CI.|
| **Aligned with tracks** | **Python** -- aligned with the SRE track; shows DevOps skills (Docker, CI, health checks, monitoring).|

**What I would talk about in an interview:**

- Why I chose FastAPI over Flask (async, auto-docs, Pydantic integration)
- How I structured the code for testability and separation of concerns
- The trade-off of SQLite vs Postgres and how the config layer makes it swappable
- How the CI pipeline catches regressions and enforces code quality
- What I would add next (rate limiting, analytics dashboard, Redis caching)

---

## License

This project is for demonstration purposes as part of the MLH Fellowship application process.