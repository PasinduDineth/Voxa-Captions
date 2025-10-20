# Voxa-Captions Development Script
# Run the application in development mode

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Voxa-Captions - Development Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Check if models are downloaded, auto-download if needed
if (-not (Test-Path "models\main.exe")) {
    Write-Host ""
    Write-Host "Models not found. Downloading required models (one-time setup)..." -ForegroundColor Yellow
    Write-Host ""
    python setup_models.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to download models!" -ForegroundColor Red
        Write-Host "Please check your internet connection." -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
    Write-Host "Models downloaded successfully!" -ForegroundColor Green
}

# Run the application
Write-Host ""
Write-Host "Starting Voxa-Captions..." -ForegroundColor Green
Write-Host ""

python caption_generator_app.py
