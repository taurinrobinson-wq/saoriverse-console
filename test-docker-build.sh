#!/bin/bash

# Test Docker build with FirstPerson Dockerfile
# This script validates the Dockerfile before pushing to Docker Hub

echo "🏗️  Testing Docker build for FirstPerson..."
echo ""

# Build with no cache to get fresh downloads
echo "Building Docker image (this may take 5-10 minutes)..."
docker build \
  -f Dockerfile.firstperson \
  -t firstperson:test \
  --no-cache \
  .

BUILD_STATUS=$?

if [ $BUILD_STATUS -eq 0 ]; then
  echo ""
  echo "✅ Build successful!"
  echo ""
  echo "Next steps:"
  echo "1. Test the image: docker run --rm firstperson:test python -c 'import fastapi; print(fastapi.__version__)'"
  echo "2. Tag for registry: docker tag firstperson:test your-registry/firstperson:latest"
  echo "3. Push to registry: docker push your-registry/firstperson:latest"
else
  echo ""
  echo "❌ Build failed with status: $BUILD_STATUS"
  echo ""
  echo "Troubleshooting:"
  echo "1. Check network connectivity to PyPI"
  echo "2. Increase pip timeouts: --default-timeout=120"
  echo "3. Use alternative PyPI mirror if available"
  echo "4. Review Dockerfile.firstperson for issues"
  exit 1
fi
