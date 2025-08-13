#!/usr/bin/env pwsh
# Full deployment script for Titanic API with automatic data extraction

param(
    [switch]$Public,
    [switch]$Help
)

if ($Help) {
    Write-Host "=== TITANIC API DEPLOYMENT SCRIPT ===" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1              # Deploy locally only"
    Write-Host "  .\deploy.ps1 -Public      # Deploy + expose publicly with ngrok"
    Write-Host "  .\deploy.ps1 -Help        # Show this help"
    Write-Host ""
    Write-Host "Requirements for public access:" -ForegroundColor Cyan
    Write-Host "  - Ngrok account: https://dashboard.ngrok.com/signup"
    Write-Host "  - Auth token configured (see README.md)"
    exit 0
}

Write-Host "=== TITANIC API DEPLOYMENT ===" -ForegroundColor Green
Write-Host "1. Extracting data from titanic.db using JOIN query..." -ForegroundColor Yellow

# Step 1: Extract data and generate init_db.sql
docker-compose --profile setup run --rm data-extractor

Write-Host "2. Starting PostgreSQL with extracted data..." -ForegroundColor Yellow

# Step 2: Start PostgreSQL (will automatically run init_db.sql)
docker-compose up postgres -d

Write-Host "3. Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep 10

Write-Host "4. Starting Titanic API..." -ForegroundColor Yellow

# Step 3: Start the API
docker-compose up titanic-api -d

Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Green
Write-Host "API available at: http://localhost:8000/docs" -ForegroundColor Cyan

if ($Public) {
    Write-Host ""
    Write-Host "=== EXPOSING API PUBLICLY ===" -ForegroundColor Green
    Write-Host "Setting up ngrok tunnel..." -ForegroundColor Yellow
    
    Write-Host "Note: You'll get a new public URL each time you run this." -ForegroundColor Yellow
    Write-Host "Starting ngrok tunnel for Docker API (requires auth token)..." -ForegroundColor Cyan
    
    # Activate virtual environment and start ngrok for the Docker API
    & ".\axaenv\Scripts\Activate.ps1"
    
    # Start ngrok to expose the Docker API running on localhost:8000
    Write-Host "Creating public tunnel to localhost:8000..." -ForegroundColor Yellow
    python -c @"
import pyngrok.ngrok as ngrok
import time
import requests

# Start ngrok tunnel
tunnel = ngrok.connect(8000, 'http')
public_url = tunnel.public_url

print()
print('🌐 PUBLIC API URLs:')
print(f'📚 Interactive Docs: {public_url}/docs')
print(f'🔗 API Base URL: {public_url}/api/v1/')
print(f'❤️ Health Check: {public_url}/health')
print()
print('🔐 Authentication required:')
print('   Username: admin, Password: secret')
print('   Username: analyst, Password: password123')
print('   Username: viewer, Password: view2024')
print()
print('Press Ctrl+C to stop the tunnel...')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('\nShutting down tunnel...')
    ngrok.disconnect(tunnel.public_url)
    ngrok.kill()
"@
} else {
    Write-Host ""
    Write-Host "For public access, run: .\deploy.ps1 -Public" -ForegroundColor Yellow
    Write-Host "Check logs with: docker-compose logs -f" -ForegroundColor Cyan
}
