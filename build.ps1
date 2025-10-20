# Voxa-Captions Build Script
# Builds a standalone Windows executable using PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Voxa-Captions - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if models directory exists and download if needed
if (-not (Test-Path "models\main.exe")) {
    Write-Host ""
    Write-Host "Whisper.cpp binaries not found. Downloading required models..." -ForegroundColor Yellow
    Write-Host ""
    python setup_models.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to download models!" -ForegroundColor Red
        Write-Host "Please check your internet connection and try again." -ForegroundColor Red
        Write-Host ""
        Write-Host "Or manually run: python setup_models.py" -ForegroundColor Yellow
        exit 1
    }
    Write-Host ""
    Write-Host "Models downloaded successfully!" -ForegroundColor Green
}

# Create spec file if it doesn't exist
if (-not (Test-Path "caption_generator.spec")) {
    Write-Host "Generating PyInstaller spec file..." -ForegroundColor Yellow
    pyi-makespec --name="VoxaCaptions" --windowed --onefile --icon=NONE caption_generator_app.py
}

# Build the executable
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Green
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

# Using one-dir for better performance and to include all models
Write-Host "Building one-directory bundle (includes all models)..." -ForegroundColor Cyan
Write-Host ""

pyinstaller --clean --noconfirm `
    --name="VoxaCaptions" `
    --windowed `
    --onedir `
    --add-data="models;models" `
    --add-data="transcription_engine.py;." `
    --hidden-import=PyQt6 `
    --hidden-import=PyQt6.QtCore `
    --hidden-import=PyQt6.QtGui `
    --hidden-import=PyQt6.QtWidgets `
    caption_generator_app.py

# Check if build was successful
if (Test-Path "dist\VoxaCaptions") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application location: dist\VoxaCaptions\" -ForegroundColor Cyan
    Write-Host "Main executable: dist\VoxaCaptions\VoxaCaptions.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Models are bundled inside the application!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To distribute the app:" -ForegroundColor Yellow
    Write-Host "  - Copy the ENTIRE 'dist\VoxaCaptions' folder" -ForegroundColor Yellow
    Write-Host "  - All models are included (~600 MB total)" -ForegroundColor Yellow
    Write-Host "  - No internet needed on target machine" -ForegroundColor Yellow
    Write-Host "  - Double-click VoxaCaptions.exe to run" -ForegroundColor Yellow
    Write-Host ""
    
    # Calculate folder size
    $folderSize = (Get-ChildItem -Path "dist\VoxaCaptions" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "Total size: $([math]::Round($folderSize, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
    Write-Host ""
}

# Pause to see results
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
