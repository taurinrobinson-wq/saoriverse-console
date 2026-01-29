FROM node:20-bullseye-slim

WORKDIR /app

# Only copy velinor-web files initially
COPY velinor-web/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy the rest of velinor-web
COPY velinor-web/ ./

# Copy only the velinor folder (the game mechanics the app needs)
COPY velinor/ ../velinor/

# Build
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
