# OP_CMS Backend Dockerfile
# Python 3.9+ Sanic backend application

# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim AS production

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "-m", "sanic", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM python:3.9-slim AS development

WORKDIR /app

# Install system dependencies including dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies including dev requirements
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    ENV=development

# Expose port for dev server
EXPOSE 8000

# Run with auto-reload
CMD ["python", "-m", "sanic", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--debug", "--auto-reload"]
