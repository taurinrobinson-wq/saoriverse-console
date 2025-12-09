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
COPY velinor-web/tailwind.config.ts ./
COPY velinor-web/eslint.config.mjs ./
RUN npm run build

# Stage 2: Runtime with both Node.js and Python
FROM node:20-alpine
WORKDIR /app

# Install Python and essential build tools
RUN apk add --no-cache python3 py3-pip curl

# Copy Next.js build
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY velinor-web/package.json ./velinor-web/

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy backend code
COPY velinor_api.py .
COPY velinor/ ./velinor/

EXPOSE 3000 8000

# Create startup script
RUN cat > /app/start.sh << 'EOF'
#!/bin/sh
set -e
# Start FastAPI in background
echo "Starting FastAPI backend on port 8000..."
python3 velinor_api.py &
API_PID=$!
sleep 2

# Start Next.js in foreground
echo "Starting Next.js frontend on port 3000..."
cd /app/velinor-web
npm start
EOF
RUN chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run startup script
CMD ["/app/start.sh"]


