# Deployment Dockerfile for FortiGate Management - OPTIMIZED
FROM python:3.12-slim

# Set environment variables
ENV UV_VERSION=0.1.19 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && curl -Ls https://astral.sh/uv/install.sh | sh \
    && mv ~/.local/bin/uv /usr/local/bin/uv \
    && chmod +x /usr/local/bin/uv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt ./

# Install dependencies
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/certs /app/static

# Copy application files in logical order
COPY app ./app
COPY tools ./tools
COPY scripts ./scripts

# Copy static files and certificates
COPY app/static/icons.db ./app/static/icons.db
COPY app/certs/ ./app/certs/

# Copy secrets (should be mounted as volumes in production)
COPY secrets ./secrets

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 10000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
