# Voxa-Captions

**Offline Audio Caption Generator for Windows**

Generate accurate word-level captions from audio files using OpenAI's Whisper model - completely offline with no internet required after setup.

## 🎯 Features

- ✅ **100% Offline Operation** - Works without internet after initial setup
- 🎙️ **Multiple Audio Formats** - Supports MP3, WAV, M4A, FLAC, OGG, AAC, WMA
- 🌍 **Multi-Language Support** - Auto-detect or choose from 100+ languages
- 📊 **Word-Level Timestamps** - Precise timing for each word
- 🎚️ **Multiple Quality Options** - Choose from 5 Whisper models
- 💾 **Local Storage** - All models stored locally
- 🖥️ **User-Friendly GUI** - Simple drag-and-drop interface
- 📄 **JSON Output** - Compatible with video editing workflows

## 📋 Requirements

### System Requirements
- Windows 10 or later (64-bit)
- At least 4GB RAM (8GB recommended for large models)
- 500MB - 5GB storage (depending on models selected)

### Software Requirements
- Python 3.8 or later
- FFmpeg (for audio conversion)

## 🚀 Quick Start

### 1. Install FFmpeg

FFmpeg is required for audio conversion:

**Option A: Using Chocolatey (Recommended)**
```powershell
choco install ffmpeg
```

**Option B: Using Scoop**
```powershell
scoop install ffmpeg
```

**Option C: Manual Installation**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract and add to your system PATH

Verify installation: `ffmpeg -version`

### 2. Run the Application

**That's it!** Just run:

```powershell
.\run_dev.ps1
```

**What happens automatically:**
- ✅ Creates virtual environment (if needed)
- ✅ Installs Python dependencies (if needed)
- ✅ **Downloads models automatically** (if not present - ~500 MB one-time download)
- ✅ Launches the application

### 3. Build Standalone Executable (Optional)

To create a distributable `.exe` file:

```powershell
.\build.ps1
```

**What happens automatically:**
- ✅ Sets up build environment
- ✅ **Downloads models if not present**
- ✅ Bundles everything into `dist\VoxaCaptions.exe`
- ✅ Ready to distribute (include the `models` folder)

**Model Auto-Downloaded:**
- `small` (466 MB) - **Default** - Best balance of speed and quality

**Want More Models?**
```powershell
python download_models.py  # Interactive selection
```

**Model Options:**
- `tiny` (75 MB) - Fastest, lowest quality
- `base` (142 MB) - Fast, decent quality
- `small` (466 MB) - **Default/Recommended** - Good balance
- `medium` (1.5 GB) - Better quality, slower
- `large-v3` (2.9 GB) - Best quality, slowest

## 🏗️ Building Standalone Executable

To create a standalone `.exe` file that can be distributed:

```powershell
.\build.ps1
```

The executable will be created in the `dist` folder.

**To distribute:**
1. Copy `VoxaCaptions.exe` from the `dist` folder
2. Copy the entire `models` folder (with downloaded models and binaries)
3. Keep them together in the same directory structure
4. No Python installation required on the target machine!

## 📖 Usage

### Basic Usage

1. **Launch the application**
   - Run `run_dev.ps1` or double-click `VoxaCaptions.exe`

2. **Select an audio file**
   - Click "Browse Audio File"
   - Choose your audio file (MP3, WAV, etc.)

3. **Choose settings**
   - **Model**: Select quality level (small recommended)
   - **Language**: Auto-detect or specify language

4. **Generate captions**
   - Click "Generate Captions"
   - Wait for transcription to complete
   - JSON file will be saved next to your audio file

### Output Format

The generated JSON file contains word-level timestamps:

```json
[
  {
    "text": "Hello",
    "startMs": 0,
    "endMs": 500,
    "timestampMs": 0,
    "confidence": 0.98
  },
  {
    "text": " world",
    "startMs": 500,
    "endMs": 1200,
    "timestampMs": 500,
    "confidence": 0.95
  }
]
```

### Command Line Usage

You can also use the transcription engine directly:

```powershell
python transcription_engine.py audio_file.mp3 small
```

## 🎨 Supported Languages

Auto-detect or choose from:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)
- And 100+ more!

## 📁 Project Structure

```
Voxa-Captions/
├── caption_generator_app.py   # Main GUI application
├── transcription_engine.py    # Core transcription logic
├── download_models.py          # Model/binary download script
├── requirements.txt            # Python dependencies
├── build.ps1                   # Build executable script
├── run_dev.ps1                 # Development run script
├── README.md                   # This file
└── models/                     # Downloaded models and binaries
    ├── main.exe                # Whisper.cpp executable
    ├── ggml-small.bin          # Whisper model files
    └── ...
```

## 🔧 Troubleshooting

### "FFmpeg not found"
- Install FFmpeg and add it to your system PATH
- Restart your terminal/PowerShell after installation

### "Model not found"
- Run `python download_models.py` to download required models
- Make sure the `models` folder contains the `.bin` files

### "Whisper.cpp executable not found"
- Run `python download_models.py` to download binaries
- Ensure `main.exe` is in the `models` folder

### Application won't start
- Check Python version: `python --version` (needs 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Try running in development mode first: `.\run_dev.ps1`

### Transcription is slow
- Use a smaller model (tiny or base)
- Close other applications to free up RAM
- Consider using a GPU-enabled version for better performance

## 🛠️ Development

### Setup Development Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download models
python download_models.py

# Run application
python caption_generator_app.py
```

### Building from Source

```powershell
# Ensure all dependencies are installed
pip install -r requirements.txt

# Build executable
.\build.ps1
```

## 📦 Dependencies

- **PyQt6** - GUI framework
- **PyInstaller** - Executable builder
- **Whisper.cpp** - Fast C++ implementation of Whisper
- **FFmpeg** - Audio conversion

## 🌟 Credits

- Based on OpenAI's Whisper model
- Uses whisper.cpp by ggerganov
- Inspired by the creator app in the tiktok-faceless project

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

This is a standalone project that can be used independently. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Ensure all requirements are met
3. Verify models are downloaded correctly

## 🎯 Use Cases

- Generate captions for videos
- Create subtitles for podcasts
- Transcribe interviews
- Create accessible content
- Language learning applications
- Content analysis

## ⚡ Performance Tips

1. **Model Selection**
   - Start with `small` model for best balance
   - Use `tiny` for quick testing
   - Use `large-v3` only for critical accuracy needs

2. **Audio Quality**
   - Clear audio = better transcription
   - Minimize background noise
   - Use mono audio when possible

3. **System Resources**
   - Close unnecessary applications
   - Ensure sufficient RAM available
   - Consider SSD for faster model loading

## 🔒 Privacy

- **No internet required** after setup
- **No data sent externally**
- All processing happens locally on your machine
- Your audio files never leave your computer

---

**Made with ❤️ for offline audio transcription**
