# Saoriverse Console - FastAPI Backend
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding items in .dockerignore)
COPY . .

# Create data directory
RUN mkdir -p /app/data_local /app/logs

# Expose port
EXPOSE 8000

# Health check - FastAPI runs on port 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI server using uvicorn
CMD ["uvicorn", "core.start:app", "--host", "0.0.0.0", "--port", "8000"]
