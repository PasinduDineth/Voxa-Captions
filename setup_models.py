"""
Auto-Download Models Script
Automatically downloads required Whisper models and binaries without user interaction.
This ensures the app can work offline after the first setup.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


# Default model to bundle with the app
DEFAULT_MODEL = "small"  # 466 MB - Good balance of speed and quality

# Whisper model URLs
MODEL_URLS = {
    "tiny": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
    "base": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
    "small": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
    "medium": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
    "large-v3": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
}

# Whisper.cpp Windows binaries - Using latest stable release with binaries
WHISPER_CPP_RELEASE_URL = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper-bin-x64.zip"


class DownloadProgress:
    """Progress reporter for downloads"""
    
    def __init__(self, filename):
        self.filename = filename
        self.last_percent = -1
    
    def __call__(self, block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, int(downloaded * 100 / total_size))
            
            if percent != self.last_percent and percent % 10 == 0:
                self.last_percent = percent
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                print(f"  {self.filename}: {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)")


def download_file_silent(url: str, dest_path: Path, description: str = None) -> bool:
    """Download a file silently"""
    if dest_path.exists():
        print(f"✓ {dest_path.name} already exists")
        return True
    
    print(f"Downloading {description or dest_path.name}...")
    try:
        urllib.request.urlretrieve(url, dest_path, DownloadProgress(dest_path.name))
        print(f"✓ Downloaded {dest_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {dest_path.name}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def download_whisper_binaries(models_dir: Path) -> bool:
    """Download pre-compiled Whisper.cpp binaries"""
    print("\n[1/2] Downloading Whisper.cpp binaries...")
    
    main_exe = models_dir / "main.exe"
    if main_exe.exists():
        print("✓ Whisper.cpp binaries already installed")
        return True
    
    zip_path = models_dir / "whisper-bin-x64.zip"
    try:
        if not download_file_silent(WHISPER_CPP_RELEASE_URL, zip_path, "Whisper.cpp binaries"):
            return False
        
        print("Extracting binaries...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        
        # Move files from subdirectory if needed
        extracted_dir = models_dir / "whisper-bin-x64"
        if extracted_dir.exists():
            for item in extracted_dir.iterdir():
                dest = models_dir / item.name
                if dest.exists():
                    dest.unlink()
                shutil.move(str(item), str(dest))
            extracted_dir.rmdir()
        
        zip_path.unlink()
        print("✓ Whisper.cpp binaries installed")
        return True
        
    except Exception as e:
        print(f"✗ Failed to install binaries: {e}")
        return False


def download_model(model_name: str, models_dir: Path) -> bool:
    """Download a specific Whisper model"""
    if model_name not in MODEL_URLS:
        print(f"✗ Unknown model: {model_name}")
        return False
    
    model_path = models_dir / f"ggml-{model_name}.bin"
    return download_file_silent(MODEL_URLS[model_name], model_path, f"Whisper {model_name} model")


def ensure_models_downloaded(models_to_download: list = None) -> bool:
    """Ensure required models are downloaded"""
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("Voxa-Captions - Auto Model Setup")
    print("="*60)
    
    if models_to_download is None:
        models_to_download = [DEFAULT_MODEL]
    
    # Download binaries
    if not download_whisper_binaries(models_dir):
        return False
    
    # Download models
    print(f"\n[2/2] Downloading Whisper models...")
    success = True
    for model in models_to_download:
        if not download_model(model, models_dir):
            success = False
    
    if success:
        print("\n" + "="*60)
        print("✓ Setup completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ Some downloads failed")
        print("="*60)
    
    return success


def main():
    """Main entry point"""
    # Check if models are already present
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    
    main_exe = models_dir / "main.exe"
    default_model = models_dir / f"ggml-{DEFAULT_MODEL}.bin"
    
    if main_exe.exists() and default_model.exists():
        print("Models already downloaded. Nothing to do.")
        return 0
    
    # Download default model
    if ensure_models_downloaded([DEFAULT_MODEL]):
        return 0
    else:
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
