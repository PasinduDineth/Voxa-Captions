@echo off
echo ========================================
echo Voxa-Captions - Development Mode
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if models are downloaded, auto-download if needed
if not exist "models\main.exe" (
    echo.
    echo Models not found. Downloading required models (one-time setup)...
    echo.
    python setup_models.py
    
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to download models!
        echo Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Models downloaded successfully!
)

REM Run the application
echo.
echo Starting Voxa-Captions...
echo.

python caption_generator_app.py

pause
