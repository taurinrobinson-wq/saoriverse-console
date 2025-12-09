# Multi-stage build for Velinor Web Game
# Stage 1: Build Next.js frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/velinor-web
COPY velinor-web/package*.json ./
RUN npm ci
COPY velinor-web/src ./src
COPY velinor-web/public ./public
COPY velinor-web/*.* ./
RUN npm run build

# Stage 2: Runtime image with Python backend
FROM python:3.12-slim
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Install Node.js for running Next.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY velinor_api.py .
COPY velinor/ ./velinor/

# Copy Next.js build from frontend builder
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY --from=frontend-builder /app/velinor-web/package.json ./velinor-web/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Start the backend (which will serve the frontend through proxying)
CMD ["python", "velinor_api.py"]
