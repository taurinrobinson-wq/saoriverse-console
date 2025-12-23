# Dockerfile.ml - ML / audio engine image
# This image installs native audio libraries and the ML/audio requirements
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install native libraries needed for audio processing and builds
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install ML/audio Python requirements
COPY requirements.ml.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.ml.txt

# Copy repository (use .dockerignore to avoid large context)
COPY . .

RUN mkdir -p /app/models /app/logs

# ML image often run as a service or invoked from orchestration; keep interactive shell as default
CMD ["bash"]
