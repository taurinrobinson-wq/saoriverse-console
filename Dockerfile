# Multi-stage build for Velinor Web Game
# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/velinor-web
COPY velinor-web/package*.json ./
RUN npm ci
COPY velinor-web/src ./src
COPY velinor-web/public ./public
COPY velinor-web/*.* ./
RUN npm run build

# Stage 2: Runtime image with both Next.js and Python
FROM node:20-alpine
WORKDIR /app

# Install Python and build tools
RUN apk add --no-cache python3 py3-pip gcc musl-dev python3-dev

# Copy Next.js build
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY --from=frontend-builder /app/velinor-web/package.json ./velinor-web/

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy backend code
COPY velinor_api.py .
COPY velinor/ ./velinor/

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q -O- http://localhost:3000 || exit 1

# Start Next.js (main process)
CMD ["sh", "-c", "cd velinor-web && npm start"]

