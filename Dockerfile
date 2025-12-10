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
RUN apk add --no-cache python3 py3-pip ffmpeg-dev nginx curl bash pkgconfig

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

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000 (Railway default, nginx will listen here)
EXPOSE 8000

# Health check - check nginx on port 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run startup script
ENTRYPOINT ["/entrypoint.sh"]


