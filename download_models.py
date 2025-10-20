"""
Download Whisper Models and Binaries
This script downloads the necessary Whisper.cpp binaries and model files
for offline transcription.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import List


# Whisper model URLs (official OpenAI models)
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
    """Simple progress reporter for downloads"""
    
    def __init__(self, filename):
        self.filename = filename
        self.last_percent = -1
    
    def __call__(self, block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, int(downloaded * 100 / total_size))
            
            if percent != self.last_percent:
                self.last_percent = percent
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '=' * filled + '-' * (bar_length - filled)
                
                # Calculate size in MB
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                
                print(f"\r{self.filename}: [{bar}] {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
        else:
            print(f"\r{self.filename}: Downloading...", end='', flush=True)


def download_file(url: str, dest_path: Path, description: str = None):
    """Download a file with progress bar"""
    if dest_path.exists():
        print(f"✓ {dest_path.name} already exists, skipping download")
        return
    
    print(f"\nDownloading {description or dest_path.name}...")
    try:
        urllib.request.urlretrieve(
            url,
            dest_path,
            DownloadProgress(dest_path.name)
        )
        print()  # New line after progress bar
        print(f"✓ Downloaded {dest_path.name}")
    except Exception as e:
        print(f"\n✗ Failed to download {dest_path.name}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        raise


def download_whisper_binaries(models_dir: Path):
    """Download pre-compiled Whisper.cpp binaries for Windows"""
    print("\n" + "="*60)
    print("STEP 1: Downloading Whisper.cpp Binaries")
    print("="*60)
    
    # Check if main.exe already exists
    main_exe = models_dir / "main.exe"
    if main_exe.exists():
        print("✓ Whisper.cpp binaries already installed")
        return
    
    # Download the ZIP file
    zip_path = models_dir / "whisper-bin-x64.zip"
    try:
        download_file(
            WHISPER_CPP_RELEASE_URL,
            zip_path,
            "Whisper.cpp Windows binaries"
        )
        
        # Extract the ZIP
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
        
        # Clean up ZIP file
        zip_path.unlink()
        
        print("✓ Whisper.cpp binaries installed successfully")
        
    except Exception as e:
        print(f"✗ Failed to install Whisper.cpp binaries: {e}")
        raise


def download_model(model_name: str, models_dir: Path):
    """Download a specific Whisper model"""
    if model_name not in MODEL_URLS:
        print(f"✗ Unknown model: {model_name}")
        print(f"Available models: {', '.join(MODEL_URLS.keys())}")
        return False
    
    model_path = models_dir / f"ggml-{model_name}.bin"
    
    try:
        download_file(
            MODEL_URLS[model_name],
            model_path,
            f"Whisper {model_name} model"
        )
        return True
    except Exception as e:
        print(f"✗ Failed to download {model_name} model: {e}")
        return False


def download_models(models: List[str], models_dir: Path):
    """Download multiple Whisper models"""
    print("\n" + "="*60)
    print("STEP 2: Downloading Whisper Models")
    print("="*60)
    
    success_count = 0
    for model in models:
        if download_model(model, models_dir):
            success_count += 1
    
    print(f"\n✓ Successfully downloaded {success_count}/{len(models)} models")


def get_model_info():
    """Display information about available models"""
    print("\nAvailable Whisper Models:")
    print("-" * 60)
    print("Model       | Size    | RAM Usage | Quality")
    print("-" * 60)
    print("tiny        | 75 MB   | ~390 MB   | Lowest (fastest)")
    print("base        | 142 MB  | ~500 MB   | Low-Medium")
    print("small       | 466 MB  | ~1.0 GB   | Good (recommended)")
    print("medium      | 1.5 GB  | ~2.6 GB   | Better")
    print("large-v3    | 2.9 GB  | ~4.7 GB   | Best (slowest)")
    print("-" * 60)


def main():
    """Main download script"""
    print("="*60)
    print("Voxa-Captions - Model & Binary Download Script")
    print("="*60)
    
    # Get models directory
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    print(f"\nInstallation directory: {models_dir}")
    
    # Show model information
    get_model_info()
    
    # Ask user which models to download
    print("\nWhich models would you like to download?")
    print("1. small only (466 MB) - Recommended for most users")
    print("2. tiny + small (541 MB) - Fast testing + good quality")
    print("3. base + small (608 MB) - Multiple quality options")
    print("4. All models (5.1 GB) - Complete package")
    print("5. Custom selection")
    print("6. Skip model download (binaries only)")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            models_to_download = ["small"]
            break
        elif choice == "2":
            models_to_download = ["tiny", "small"]
            break
        elif choice == "3":
            models_to_download = ["base", "small"]
            break
        elif choice == "4":
            models_to_download = list(MODEL_URLS.keys())
            break
        elif choice == "5":
            print("\nAvailable models: tiny, base, small, medium, large-v3")
            models_input = input("Enter model names (comma-separated): ").strip()
            models_to_download = [m.strip() for m in models_input.split(",")]
            if all(m in MODEL_URLS for m in models_to_download):
                break
            else:
                print("Invalid model name(s). Please try again.")
        elif choice == "6":
            models_to_download = []
            break
        else:
            print("Invalid choice. Please enter 1-6.")
    
    try:
        # Download Whisper.cpp binaries
        download_whisper_binaries(models_dir)
        
        # Download selected models
        if models_to_download:
            download_models(models_to_download, models_dir)
        else:
            print("\nSkipping model download as requested.")
        
        print("\n" + "="*60)
        print("✓ INSTALLATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now run the Voxa-Captions application.")
        print("To download additional models later, run this script again.")
        
    except Exception as e:
        print("\n" + "="*60)
        print("✗ INSTALLATION FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("\nPlease check your internet connection and try again.")
        sys.exit(1)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
