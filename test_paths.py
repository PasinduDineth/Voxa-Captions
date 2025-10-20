"""
Quick test to verify model paths in the bundled exe
"""
import sys
from pathlib import Path

print("=" * 60)
print("Model Path Detection Test")
print("=" * 60)

# Check if running as frozen
is_frozen = getattr(sys, 'frozen', False)
print(f"\nRunning as frozen exe: {is_frozen}")

if is_frozen:
    print(f"sys.executable: {sys.executable}")
    exe_parent = Path(sys.executable).parent
    print(f"Exe parent: {exe_parent}")
    
    # Check _internal
    internal_dir = exe_parent / "_internal"
    print(f"\n_internal exists: {internal_dir.exists()}")
    
    if internal_dir.exists():
        models_dir = internal_dir / "models"
        print(f"models folder exists: {models_dir.exists()}")
        
        if models_dir.exists():
            print(f"\nModels found:")
            for file in models_dir.glob("*.bin"):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  - {file.name} ({size_mb:.1f} MB)")
            
            for file in models_dir.glob("*.exe"):
                print(f"  - {file.name}")
else:
    print(f"__file__: {__file__}")
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    print(f"models folder: {models_dir}")
    print(f"models exists: {models_dir.exists()}")

print("\n" + "=" * 60)
input("Press Enter to exit...")
