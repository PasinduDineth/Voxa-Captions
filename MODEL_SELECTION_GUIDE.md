# Model Selection Guide

## 📦 What's Bundled by Default

When you build the app with `.\build.ps1`, only the **small** model is automatically downloaded and bundled:

- ✅ **small** (466 MB) - Best balance of speed and quality

## 🎯 Why Only One Model?

To keep the distribution size reasonable (~551 MB), only the recommended model is included. The small model provides excellent quality for most use cases.

## 📥 How to Bundle Additional Models

If you want to include more models in your build:

### Option 1: Download Before Building

```powershell
# Download additional models interactively
python download_models.py

# Select the models you want (e.g., tiny, base, medium)
# Then build
.\build.ps1
```

### Option 2: Manual Download

1. Download models from Hugging Face:
   - https://huggingface.co/ggerganov/whisper.cpp/tree/main

2. Place `.bin` files in the `models/` folder:
   ```
   models/
   ├── ggml-tiny.bin       (optional)
   ├── ggml-base.bin       (optional)
   ├── ggml-small.bin      (included by default)
   ├── ggml-medium.bin     (optional)
   └── ggml-large-v3.bin   (optional)
   ```

3. Build:
   ```powershell
   .\build.ps1
   ```

All models in the `models/` folder will be bundled!

## 📊 Model Comparison

| Model | Size | RAM | Speed | Quality | Use Case |
|-------|------|-----|-------|---------|----------|
| tiny | 75 MB | ~390 MB | Fastest | Lowest | Quick testing |
| base | 142 MB | ~500 MB | Fast | Good | Good speed/quality |
| **small** | **466 MB** | **~1 GB** | **Balanced** | **Very Good** | **Recommended** |
| medium | 1.5 GB | ~2.6 GB | Slow | Better | High accuracy |
| large-v3 | 2.9 GB | ~4.7 GB | Slowest | Best | Professional |

## 🎨 What Users See

The app automatically detects which models are bundled and only shows those in the dropdown.

### If only small is bundled:
```
Whisper Model: [small (466 MB, balanced) ✓]
```

### If multiple models are bundled:
```
Whisper Model: [tiny (75 MB, fastest, lowest quality)      ]
               [base (142 MB, fast, good quality)         ]
               [small (466 MB, balanced) ✓                ]
               [medium (1.5 GB, slower, better quality)   ]
```

## 💡 Recommendations

### For Most Users (Default)
- **small** model only
- Distribution size: ~551 MB
- Good for 95% of use cases

### For Professional Use
- Include **small** + **medium**
- Distribution size: ~2 GB
- Covers all quality needs

### For Complete Package
- Include all 5 models
- Distribution size: ~5.6 GB
- Users can choose optimal model for each task

## 🚀 Quick Build Examples

### Default (small only):
```powershell
.\build.ps1
```

### With multiple models:
```powershell
# 1. Download models you want
python download_models.py
# Choose: base, small, medium

# 2. Build
.\build.ps1

# Result: All selected models bundled!
```

## ✅ After Building

Check what's bundled:
```powershell
dir dist\VoxaCaptions\_internal\models\*.bin
```

You should see all the `.bin` files you downloaded.

---

**TIP**: For distribution, start with just the small model. Users can always download additional models later if needed (though currently the app doesn't support post-install model downloads).
