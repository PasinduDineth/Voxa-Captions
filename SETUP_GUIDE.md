# Voxa-Captions - Installation & Setup Guide

## 🚀 Complete Setup Process

This guide will help you set up Voxa-Captions with all required models bundled for offline use.

---

## 📋 Prerequisites

### 1. Install Python
- Download Python 3.8+ from https://www.python.org/downloads/
- ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify: `python --version`

### 2. Install FFmpeg
FFmpeg is required for audio conversion. Choose ONE method:

**Option A - Chocolatey (Recommended)**
```powershell
choco install ffmpeg
```

**Option B - Scoop**
```powershell
scoop install ffmpeg
```

**Option C - Manual**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

Verify installation: `ffmpeg -version`

---

## 🎯 Method 1: Build Standalone Executable (Recommended)

This method creates a single `.exe` file with all models bundled.

### Step 1: Navigate to Project
```powershell
cd "c:\Users\pasin\Documents\tiktok-faceless\Voxa-Captions"
```

### Step 2: Run Build Script
```powershell
.\build.ps1
```

**What happens:**
1. ✅ Creates virtual environment
2. ✅ Installs Python dependencies
3. ✅ **Automatically downloads models** (if not present)
4. ✅ Builds `VoxaCaptions.exe`
5. ✅ Bundles everything together

### Step 3: Find Your Executable
```
dist\VoxaCaptions.exe  ← Your standalone app
```

### Step 4: Distribution
To share with others:
```
Your-Distribution-Folder/
├── VoxaCaptions.exe
└── models/
    ├── main.exe
    ├── whisper.dll
    └── ggml-small.bin (and other models)
```

**Important**: The `models` folder must be in the same directory as `VoxaCaptions.exe`!

---

## 🛠️ Method 2: Development Mode

Run directly from Python (good for testing and development).

### Step 1: Navigate to Project
```powershell
cd "c:\Users\pasin\Documents\tiktok-faceless\Voxa-Captions"
```

### Step 2: Run Development Script
```powershell
.\run_dev.ps1
```

**What happens:**
1. ✅ Creates virtual environment (if needed)
2. ✅ Installs dependencies (if needed)
3. ✅ **Automatically downloads models** (if not present)
4. ✅ Launches the application

---

## 📦 Method 3: Manual Model Setup

If you prefer to download models manually first:

```powershell
# Download models (interactive, choose which models to download)
python download_models.py

# OR download default model only (small - 466 MB)
python setup_models.py
```

Then run:
```powershell
.\run_dev.ps1
```

---

## 🔍 Verify Installation

Run the installation checker:
```powershell
python check_installation.py
```

This will verify:
- ✅ Python version
- ✅ Dependencies installed
- ✅ FFmpeg available
- ✅ Whisper binaries present
- ✅ Models downloaded

---

## 📂 What Gets Downloaded

### Whisper.cpp Binaries (~10 MB)
- `main.exe` - Transcription engine
- `whisper.dll` - Dependencies
- Other support files

### Models (Choose One or More)

| Model | Size | Speed | Quality | Auto-Downloaded |
|-------|------|-------|---------|-----------------|
| tiny | 75 MB | Fastest | Lowest | No |
| base | 142 MB | Fast | Good | No |
| **small** | **466 MB** | **Balanced** | **Very Good** | **✅ Yes** |
| medium | 1.5 GB | Slow | Better | No |
| large-v3 | 2.9 GB | Slowest | Best | No |

**Default**: The `small` model is automatically downloaded as it offers the best balance.

---

## 🎯 First Run Experience

### Option A: Built Executable
1. Double-click `VoxaCaptions.exe`
2. If models not found → App prompts to download
3. Click "Yes" to download (~500 MB, one-time)
4. Wait for download to complete
5. App launches and works offline forever!

### Option B: Development Mode
1. Run `.\run_dev.ps1`
2. Script automatically downloads models if needed
3. App launches when ready

---

## 🌐 Internet Requirements

### ✅ **One-Time Internet Required For:**
- Initial model download (~500 MB for default setup)
- Installing Python packages
- Downloading Whisper.cpp binaries

### ✅ **After Setup - 100% Offline:**
- All transcription happens locally
- No API calls
- No data sent externally
- Complete privacy

---

## 🎨 Usage After Setup

1. **Launch app** (`.exe` or `run_dev.ps1`)
2. **Browse** for audio file
3. **Select** model and language
4. **Click** "Generate Captions"
5. **Get** JSON file next to your audio

Output format:
```json
[
  {
    "text": "word",
    "startMs": 0,
    "endMs": 500,
    "timestampMs": 0,
    "confidence": 0.95
  }
]
```

---

## 🔧 Troubleshooting

### "Python not found"
- Install Python and check "Add to PATH"
- Restart PowerShell/terminal

### "FFmpeg not found"
- Install FFmpeg (see prerequisites)
- Restart PowerShell/terminal
- Verify: `ffmpeg -version`

### "Failed to download models"
- Check internet connection
- Try manual download: `python setup_models.py`
- Check firewall/antivirus settings

### "Cannot run scripts" (PowerShell)
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Model not found" error in app
- Run: `python setup_models.py`
- Or use: `python download_models.py` for more options

---

## 🎯 Quick Commands Reference

```powershell
# Check installation status
python check_installation.py

# Download default model only
python setup_models.py

# Download specific models (interactive)
python download_models.py

# Run in development mode
.\run_dev.ps1

# Build standalone executable
.\build.ps1

# Direct transcription (command line)
python transcription_engine.py audio.mp3 small
```

---

## 📊 Storage Requirements

### Minimal Setup (Default)
- Python + dependencies: ~200 MB
- Whisper.cpp binaries: ~10 MB
- Small model: ~466 MB
- **Total: ~680 MB**

### Full Setup (All Models)
- Python + dependencies: ~200 MB
- Whisper.cpp binaries: ~10 MB
- All 5 models: ~5.1 GB
- **Total: ~5.3 GB**

### Built Executable
- VoxaCaptions.exe: ~100 MB
- Models folder: ~476 MB (with small model)
- **Total: ~580 MB**

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed and in PATH
- [ ] Project files downloaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Models downloaded
- [ ] App launches successfully
- [ ] Can transcribe audio files
- [ ] JSON output generated

---

## 🆘 Still Having Issues?

1. Run `python check_installation.py` for diagnosis
2. Check the main README.md for detailed documentation
3. Verify all prerequisites are met
4. Try manual model download: `python setup_models.py`

---

**Your app is now ready to work 100% offline! 🎉**
