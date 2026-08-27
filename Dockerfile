# syntax=docker/dockerfile:1
# ---------- Multi-stage build: Stage 1 — Build environment ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies if needed (none required for pure Python)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ---------- Stage 2 — Runtime image ----------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only the installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Ensure local bin directory is on PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY .env.example ./.env

# Create a non-root user for security
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app && \
    chown -R app:app /app

USER app

EXPOSE 8000

# Run with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]