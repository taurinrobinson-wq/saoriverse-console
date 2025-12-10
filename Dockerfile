# ---------- Frontend build stage ----------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/velinor-web

# Install dependencies  
COPY velinor-web/package*.json ./
RUN npm ci

# Copy source files
COPY velinor-web/src ./src
COPY velinor-web/public ./public
COPY velinor-web/tsconfig.json ./
COPY velinor-web/next.config.ts ./
COPY velinor-web/postcss.config.mjs ./
COPY velinor-web/eslint.config.mjs ./

# Build Next.js app
RUN npm run build


# ---------- Runtime stage ----------
FROM node:20-alpine

WORKDIR /app

# Install Python, nginx, ffmpeg
RUN apk add --no-cache python3 py3-pip ffmpeg-dev nginx curl bash

# Create Python venv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy and install Python deps
COPY requirements-game.txt .
RUN pip install --upgrade pip && pip install -r requirements-game.txt

# Copy backend
COPY velinor_api.py .
COPY velinor/ ./velinor/

# Copy frontend build
COPY --from=frontend-builder /app/velinor-web ./velinor-web

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 8000 (Railway default, nginx will listen here)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Simple startup: run all 3 services, with nginx in foreground
CMD ["sh", "-c", "cd velinor-web && npm start > /tmp/frontend.log 2>&1 & python3 velinor_api.py > /tmp/api.log 2>&1 & sleep 3 && sed -i 's/listen 5000/listen 8000/' /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"]


