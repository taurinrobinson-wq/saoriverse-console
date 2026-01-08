# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
# By default do not serve the static chat HTML from this container. Static hosting is recommended for the
# public site; set SERVE_STATIC_CHAT=1 in env to allow this container to serve `templates/chat.html` for dev.
ENV SERVE_STATIC_CHAT=0
CMD ["python", "-m", "uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "30"]