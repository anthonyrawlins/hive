FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Environment variables with production defaults
ENV DATABASE_URL=postgresql://hive:hive@postgres:5432/hive
ENV REDIS_URL=redis://redis:6379/0
ENV LOG_LEVEL=info
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app:/app/ccli_src

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy CCLI source code for CLI agent integration
COPY ccli_src /app/ccli_src

# Create non-root user
RUN useradd -m -u 1000 hive && chown -R hive:hive /app
USER hive

# Expose port
EXPOSE 8000

# Enhanced health check with longer startup period
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Run the application with production settings
CMD ["uvicorn", "app.main:socket_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]