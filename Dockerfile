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

# Stage 2: Runtime with Node.js
FROM node:20-alpine
WORKDIR /app

# Copy Next.js build and dependencies
COPY --from=frontend-builder /app/velinor-web/.next ./velinor-web/.next
COPY --from=frontend-builder /app/velinor-web/node_modules ./velinor-web/node_modules
COPY --from=frontend-builder /app/velinor-web/public ./velinor-web/public
COPY velinor-web/package.json ./velinor-web/

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget -q -O- http://localhost:3000 || exit 1

# Start Next.js
CMD ["sh", "-c", "cd velinor-web && npm start"]


