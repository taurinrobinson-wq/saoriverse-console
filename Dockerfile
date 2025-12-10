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


# ---------- Backend stage ----------
FROM node:20-alpine AS backend
WORKDIR /app

# Install Python + tools + build dependencies for PyAV
RUN apk add --no-cache python3 py3-pip curl bash pkg-config ffmpeg-dev

# Create virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy backend files
COPY requirements-game.txt .
COPY velinor_api.py .
COPY velinor/ ./velinor/

# Install Python dependencies inside venv
RUN pip install --upgrade pip && \
    pip install -r requirements-game.txt

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY velinor-web/package.json ./velinor-web/

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start both services
CMD ["sh", "-c", "python3 velinor_api.py & cd velinor-web && npm start"]


