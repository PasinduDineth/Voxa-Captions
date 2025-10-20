"""
Test Script for Voxa-Captions
Verifies that all components are properly installed and configured.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is adequate"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Too old!")
        print("  Required: Python 3.8 or later")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")
    
    packages = {
        'PyQt6': 'PyQt6',
        'PyInstaller': 'pyinstaller'
    }
    
    all_installed = True
    for display_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {display_name} - Installed")
        except ImportError:
            print(f"✗ {display_name} - Not installed")
            all_installed = False
    
    if not all_installed:
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return all_installed


def check_ffmpeg():
    """Check if FFmpeg is available"""
    print("\nChecking FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg - Installed")
            print(f"  {version_line}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ FFmpeg - Not found")
    print("  Install FFmpeg:")
    print("    Option 1: choco install ffmpeg")
    print("    Option 2: scoop install ffmpeg")
    print("    Option 3: Download from https://ffmpeg.org/download.html")
    return False


def check_whisper_binaries():
    """Check if Whisper.cpp binaries are downloaded"""
    print("\nChecking Whisper.cpp binaries...")
    
    models_dir = Path(__file__).parent / "models"
    main_exe = models_dir / "main.exe"
    
    if main_exe.exists():
        print(f"✓ Whisper.cpp - Installed")
        print(f"  Location: {main_exe}")
        return True
    else:
        print("✗ Whisper.cpp - Not found")
        print("  Run: python download_models.py")
        return False


def check_models():
    """Check which Whisper models are downloaded"""
    print("\nChecking Whisper models...")
    
    models_dir = Path(__file__).parent / "models"
    models = {
        'tiny': 'ggml-tiny.bin',
        'base': 'ggml-base.bin',
        'small': 'ggml-small.bin',
        'medium': 'ggml-medium.bin',
        'large-v3': 'ggml-large-v3.bin'
    }
    
    found_models = []
    for name, filename in models.items():
        model_path = models_dir / filename
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"✓ {name:10} - {size_mb:.1f} MB")
            found_models.append(name)
        else:
            print(f"  {name:10} - Not downloaded")
    
    if found_models:
        print(f"\n  Found {len(found_models)} model(s)")
        return True
    else:
        print("\n✗ No models found")
        print("  Run: python download_models.py")
        return False


def check_project_files():
    """Check if all project files are present"""
    print("\nChecking project files...")
    
    required_files = [
        'caption_generator_app.py',
        'transcription_engine.py',
        'download_models.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_present = True
    for filename in required_files:
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - Missing!")
            all_present = False
    
    return all_present


def print_summary(results):
    """Print final summary"""
    print("\n" + "="*60)
    print("INSTALLATION CHECK SUMMARY")
    print("="*60)
    
    all_ok = all(results.values())
    
    for check, status in results.items():
        symbol = "✓" if status else "✗"
        status_text = "OK" if status else "NEEDS ATTENTION"
        print(f"{symbol} {check:30} {status_text}")
    
    print("="*60)
    
    if all_ok:
        print("\n🎉 All checks passed! You're ready to use Voxa-Captions.")
        print("\nNext steps:")
        print("  1. Run: .\\run_dev.ps1")
        print("  2. Or build: .\\build.ps1")
    else:
        print("\n⚠️  Some components are missing or need attention.")
        print("\nRecommended actions:")
        
        if not results['Python Version']:
            print("  1. Install Python 3.8 or later")
        
        if not results['Python Dependencies']:
            print("  2. Run: pip install -r requirements.txt")
        
        if not results['FFmpeg']:
            print("  3. Install FFmpeg (see above for options)")
        
        if not results['Whisper Binaries'] or not results['Whisper Models']:
            print("  4. Run: python download_models.py")
    
    print()


def main():
    """Run all checks"""
    print("="*60)
    print("Voxa-Captions - Installation Check")
    print("="*60)
    print()
    
    results = {
        'Python Version': check_python_version(),
        'Python Dependencies': check_dependencies(),
        'FFmpeg': check_ffmpeg(),
        'Whisper Binaries': check_whisper_binaries(),
        'Whisper Models': check_models(),
        'Project Files': check_project_files()
    }
    
    print_summary(results)


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
