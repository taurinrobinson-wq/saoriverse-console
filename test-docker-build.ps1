# Test Docker build for FirstPerson (Windows PowerShell)
# This script validates the Dockerfile before pushing

Write-Host "🏗️  Testing Docker build for FirstPerson..." -ForegroundColor Cyan
Write-Host ""

# Build with no cache to get fresh downloads
Write-Host "Building Docker image (this may take 5-10 minutes)..." -ForegroundColor Yellow

$buildProcess = & docker build `
  -f Dockerfile.firstperson `
  -t firstperson:test `
  --no-cache `
  .

if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "✅ Build successful!" -ForegroundColor Green
  Write-Host ""
  Write-Host "Next steps:" -ForegroundColor Cyan
  Write-Host "1. Test the image:"
  Write-Host "   docker run --rm firstperson:test python -c 'import fastapi; print(fastapi.__version__)'"
  Write-Host ""
  Write-Host "2. Tag for registry:"
  Write-Host "   docker tag firstperson:test your-registry/firstperson:latest"
  Write-Host ""
  Write-Host "3. Push to registry:"
  Write-Host "   docker push your-registry/firstperson:latest"
  Write-Host ""
  Write-Host "4. Run container:"
  Write-Host "   docker run -p 8000:8000 -p 3001:3001 firstperson:test"
} else {
  Write-Host ""
  Write-Host "❌ Build failed with status: $LASTEXITCODE" -ForegroundColor Red
  Write-Host ""
  Write-Host "Troubleshooting:" -ForegroundColor Yellow
  Write-Host "1. Check network connectivity to PyPI"
  Write-Host "2. Verify Dockerfile.firstperson syntax"
  Write-Host "3. Check if all required files exist:"
  Write-Host "   - requirements-backend.txt"
  Write-Host "   - firstperson_backend.py"
  Write-Host "   - nginx.firstperson.conf"
  Write-Host "   - entrypoint.firstperson.sh"
  Write-Host "4. Try with increased timeout: --default-timeout=120"
  Write-Host "5. Check docker daemon is running"
  exit 1
}
