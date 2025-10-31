# Emotional OS - Railway Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding items in .dockerignore)
COPY . .

# Create data directory if needed (since we're excluding the external drive reference)
RUN mkdir -p /app/data_local

# Expose port
EXPOSE $PORT

# Health check - Streamlit runs on PORT env var, no built-in health endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=5)" || exit 1

# Default command - can be overridden by Railway
CMD ["python", "start.py"]