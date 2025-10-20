# Voxa-Captions - Quick Start Guide

## For First-Time Users

### Step 1: Install Python
1. Download Python 3.8 or later from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation: Open PowerShell and type `python --version`

### Step 2: Install FFmpeg
Choose ONE method:

**Method A - Using Chocolatey (Easiest)**
```powershell
# Install Chocolatey first (if not installed)
# Visit https://chocolatey.org/install

# Then install FFmpeg
choco install ffmpeg
```

**Method B - Using Scoop**
```powershell
# Install Scoop first (if not installed)
# Visit https://scoop.sh

# Then install FFmpeg
scoop install ffmpeg
```

**Method C - Manual Installation**
1. Go to https://ffmpeg.org/download.html
2. Download the Windows build
3. Extract to a folder (e.g., `C:\ffmpeg`)
4. Add `C:\ffmpeg\bin` to your system PATH

### Step 3: Download Models
1. Open PowerShell in the Voxa-Captions folder
2. Run: `python download_models.py`
3. Choose option 1 (small model - recommended)
4. Wait for download to complete

### Step 4: Run the App
```powershell
.\run_dev.ps1
```

That's it! The app will open and you can start generating captions.

## For Advanced Users

### Build Standalone Executable
```powershell
.\build.ps1
```

The executable will be in `dist\VoxaCaptions.exe`

### Command Line Usage
```powershell
python transcription_engine.py your_audio.mp3 small
```

## Common Issues

**"Python not found"**
- Install Python and check "Add to PATH" during installation
- Restart PowerShell after installation

**"FFmpeg not found"**
- Install FFmpeg using one of the methods above
- Restart PowerShell after installation
- Verify: `ffmpeg -version`

**"Model not found"**
- Run `python download_models.py` first
- Make sure models folder has `.bin` files

**"Cannot run scripts"**
- Open PowerShell as Administrator
- Run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Try again

## Need Help?

Check the full README.md for:
- Detailed documentation
- Troubleshooting guide
- Advanced features
- API reference
