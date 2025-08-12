#!/usr/bin/env pwsh
# Full deployment script for Titanic API with automatic data extraction

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
Write-Host "Check logs with: docker-compose logs -f" -ForegroundColor Cyan
