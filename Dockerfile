# Multi-stage build for Velinor Web Game
# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/velinor-web
COPY velinor-web/package*.json ./
RUN npm ci
COPY velinor-web/src ./src
COPY velinor-web/public ./public
COPY velinor-web/tsconfig.json ./
COPY velinor-web/next.config.ts ./
COPY velinor-web/postcss.config.mjs ./
COPY velinor-web/eslint.config.mjs ./
RUN npm run build

# Stage 2: Runtime with both Node.js and Python
FROM node:20-alpine
WORKDIR /app

# Install Python and curl
RUN apk add --no-cache python3 py3-pip curl bash

# Copy Next.js build
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY velinor-web/package.json ./velinor-web/

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy backend code
COPY velinor_api.py .
COPY velinor/ ./velinor/

EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start both services
CMD ["sh", "-c", "python3 velinor_api.py & cd /app/velinor-web && npm start"]


