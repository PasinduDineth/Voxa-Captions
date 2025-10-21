"""
Transcription Engine Module
Handles audio transcription using Whisper.cpp with Python bindings.
Generates caption JSON files compatible with the creator app format.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import tempfile


class TranscriptionEngine:
    """
    Engine for transcribing audio files using Whisper.cpp.
    All models are stored and run locally for offline operation.
    """
    
    def __init__(self, model_name: str = "small"):
        """
        Initialize the transcription engine.
        
        Args:
            model_name: Name of the Whisper model to use (tiny, base, small, medium, large-v3)
        """
        self.model_name = model_name
        
        # Determine the base directory (works for both dev and bundled exe)
        if getattr(sys, 'frozen', False):
            # Running as bundled exe (PyInstaller)
            # For --onedir, files added with --add-data go to _internal
            if hasattr(sys, '_MEIPASS'):
                # One-file mode (shouldn't happen but handle it)
                base_dir = Path(sys._MEIPASS)
            else:
                # One-dir mode - models are in _internal folder
                base_dir = Path(sys.executable).parent / "_internal"
        else:
            # Running as script - use script directory
            base_dir = Path(__file__).parent
        
        self.models_dir = base_dir / "models"
        
        # Locate model file
        self.model_path = self.models_dir / f"ggml-{model_name}.bin"
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model '{model_name}' not found at {self.model_path}. "
                f"Base dir: {base_dir}\n"
                f"Models dir exists: {self.models_dir.exists()}\n"
                f"Available: {list(self.models_dir.glob('*.bin')) if self.models_dir.exists() else 'N/A'}"
            )
        
        # Locate whisper.cpp executable
        self.whisper_exe = self._find_whisper_executable()
        if not self.whisper_exe:
            raise FileNotFoundError(
                "Whisper.cpp executable not found. Please ensure whisper.cpp is built "
                "and main.exe is available in the models directory."
            )
    
    def _find_whisper_executable(self) -> Optional[Path]:
        """Find the whisper.cpp main executable"""
        # Check in models directory
        exe_path = self.models_dir / "main.exe"
        if exe_path.exists():
            return exe_path
        
        # Check in whisper.cpp subdirectory
        exe_path = self.models_dir / "whisper.cpp" / "main.exe"
        if exe_path.exists():
            return exe_path
        
        # Check if bundled with the app
        if hasattr(sys, '_MEIPASS'):
            exe_path = Path(sys._MEIPASS) / "models" / "main.exe"
            if exe_path.exists():
                return exe_path
        
        return None
    
    def _convert_audio_to_wav(self, audio_path: str) -> str:
        """
        Convert audio to 16kHz WAV format required by Whisper.
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Path to the converted WAV file
        """
        # Create temporary WAV file
        temp_dir = tempfile.gettempdir()
        audio_name = Path(audio_path).stem
        wav_path = os.path.join(temp_dir, f"{audio_name}_16khz.wav")
        
        # Use ffmpeg to convert
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",      # Mono
            "-c:a", "pcm_s16le",  # PCM 16-bit encoding
            "-y",            # Overwrite output file
            wav_path
        ]
        
        try:
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            return wav_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to convert audio file. Make sure ffmpeg is installed.\n"
                f"Error: {e.stderr.decode()}"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg and add it to your PATH."
            )
    
    def transcribe_audio(self, audio_path: str, language: str = "auto") -> List[Dict]:
        """
        Transcribe an audio file and return captions in the required JSON format.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (auto, en, es, fr, etc.)
            
        Returns:
            List of caption dictionaries with format:
            {
                "text": str,
                "startMs": int,
                "endMs": int,
                "timestampMs": int,
                "confidence": float
            }
        """
        # Convert audio to WAV format
        wav_path = self._convert_audio_to_wav(audio_path)
        
        try:
            # Run whisper.cpp with word-level timestamps
            whisper_cmd = [
                str(self.whisper_exe),
                "-m", str(self.model_path),
                "-f", wav_path,
                "-oj",  # Output JSON
                "-ojf",  # Output JSON with full details including word timestamps
                "-ml", "1",  # Max line length (word-level)
                "-l", language,  # Language (can be 'auto' for auto-detect)
            ]
            
            # Execute whisper.cpp
            result = subprocess.run(
                whisper_cmd,
                capture_output=True,
                text=False,  # Get bytes instead of text to handle encoding properly
                cwd=str(self.models_dir),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode != 0:
                # Decode stderr with error handling for international characters
                try:
                    stderr_text = result.stderr.decode('utf-8')
                except UnicodeDecodeError:
                    stderr_text = result.stderr.decode('utf-8', errors='replace')
                
                raise RuntimeError(
                    f"Whisper transcription failed:\n{stderr_text}"
                )
            
            # Parse whisper output and convert to our caption format
            captions = self._parse_whisper_output(wav_path)
            
            return captions
            
        finally:
            # Clean up temporary WAV file
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass  # Best effort cleanup
    
    def _parse_whisper_output(self, wav_path: str) -> List[Dict]:
        """
        Parse whisper.cpp JSON output and convert to our caption format.
        
        Args:
            wav_path: Path to the WAV file (used to find JSON output)
            
        Returns:
            List of caption dictionaries
        """
        # Whisper.cpp creates a JSON file with the same name as the WAV
        json_path = Path(wav_path).with_suffix('.wav.json')
        
        if not json_path.exists():
            raise RuntimeError(
                f"Whisper output JSON not found at {json_path}"
            )
        
        try:
            # Read as binary first to properly handle UTF-8
            with open(json_path, 'rb') as f:
                raw_content = f.read()
            
            # Decode UTF-8 properly
            try:
                text_content = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, try UTF-8 with BOM
                try:
                    text_content = raw_content.decode('utf-8-sig')
                except UnicodeDecodeError:
                    # Last resort: replace bad characters
                    text_content = raw_content.decode('utf-8', errors='replace')
            
            whisper_data = json.loads(text_content)
            
            captions = []
            
            # Debug: Save a copy of the whisper output for inspection if captions end up empty
            debug_json_path = Path(wav_path).with_suffix('.wav.debug.json')
            
            # Extract transcription segments
            # whisper.cpp JSON format has a 'transcription' array with segments
            if 'transcription' in whisper_data:
                for segment in whisper_data['transcription']:
                    # whisper.cpp with -ojf creates 'tokens' array with word-level timestamps
                    if 'tokens' in segment:
                        for token_data in segment['tokens']:
                            # Skip special tokens (like [_TT_xxx], [_BEG_], etc.)
                            token_text = token_data.get('text', '')
                            if (token_text.startswith('[_') and token_text.endswith(']')) or not token_text.strip():
                                continue
                            
                            # Get offsets (in milliseconds)
                            offsets = token_data.get('offsets', {})
                            start_ms = offsets.get('from', 0)
                            end_ms = offsets.get('to', 0)
                            
                            caption = {
                                "text": token_text,
                                "startMs": start_ms,
                                "endMs": end_ms,
                                "timestampMs": start_ms,
                                "confidence": token_data.get('p', 0.95)
                            }
                            captions.append(caption)
                    
                    # Check for word-level timestamps (alternative format)
                    elif 'words' in segment:
                        for word_data in segment['words']:
                            caption = {
                                "text": word_data.get('word', word_data.get('text', '')),
                                "startMs": int(word_data.get('start', word_data.get('t0', 0)) * 1000),
                                "endMs": int(word_data.get('end', word_data.get('t1', 0)) * 1000),
                                "timestampMs": int(word_data.get('start', word_data.get('t0', 0)) * 1000),
                                "confidence": word_data.get('confidence', word_data.get('p', 0.95))
                            }
                            captions.append(caption)
                    
                    # Fallback: Use segment offsets with text splitting
                    elif 'text' in segment:
                        text = segment['text'].strip()
                        if not text:
                            continue
                            
                        words = text.split()
                        # Get segment timing from offsets (in milliseconds)
                        offsets = segment.get('offsets', {})
                        start_ms = offsets.get('from', 0)
                        end_ms = offsets.get('to', 0)
                        
                        duration_per_word = (end_ms - start_ms) / max(len(words), 1)
                        
                        for i, word in enumerate(words):
                            word_start = start_ms + int(i * duration_per_word)
                            word_end = word_start + int(duration_per_word)
                            
                            caption = {
                                "text": word,
                                "startMs": word_start,
                                "endMs": word_end,
                                "timestampMs": word_start,
                                "confidence": 0.95  # Default confidence
                            }
                            captions.append(caption)
            
            # If no captions were extracted, save debug info
            if len(captions) == 0:
                try:
                    with open(debug_json_path, 'w', encoding='utf-8') as f:
                        json.dump(whisper_data, f, indent=2, ensure_ascii=False)
                    raise RuntimeError(
                        f"No captions extracted from whisper output. "
                        f"Debug file saved to: {debug_json_path}\n"
                        f"Whisper data keys: {list(whisper_data.keys())}\n"
                        f"Please check the debug file to see the actual whisper.cpp output format."
                    )
                except json.JSONDecodeError:
                    pass
            
            # Clean up JSON file
            try:
                os.remove(json_path)
            except:
                pass
            
            return captions
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Whisper JSON output: {e}")
        except Exception as e:
            raise RuntimeError(f"Error processing transcription: {e}")


# Standalone test function
def test_transcription(audio_file: str, model: str = "small"):
    """Test the transcription engine with an audio file"""
    print(f"Testing transcription with model: {model}")
    print(f"Audio file: {audio_file}")
    
    engine = TranscriptionEngine(model_name=model)
    captions = engine.transcribe_audio(audio_file, language="auto")
    
    print(f"\nGenerated {len(captions)} caption segments:")
    for i, caption in enumerate(captions[:10]):  # Show first 10
        print(f"{i+1}. {caption['text']} ({caption['startMs']}ms - {caption['endMs']}ms)")
    
    if len(captions) > 10:
        print(f"... and {len(captions) - 10} more segments")
    
    # Save to JSON
    output_path = Path(audio_file).with_suffix('.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    
    print(f"\nCaptions saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcription_engine.py <audio_file> [model]")
        print("Example: python transcription_engine.py audio.mp3 small")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "small"
    
    test_transcription(audio_file, model)
