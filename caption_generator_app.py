"""
Voxa-Captions: Offline Audio Caption Generator
A standalone Windows application for generating caption JSON files from audio.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon
import json
import subprocess
from transcription_engine import TranscriptionEngine


class TranscriptionThread(QThread):
    """Background thread for running transcription without blocking UI"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    file_completed = pyqtSignal(int, int, str)  # current, total, filename
    
    def __init__(self, audio_paths, model_name, language):
        super().__init__()
        self.audio_paths = audio_paths if isinstance(audio_paths, list) else [audio_paths]
        self.model_name = model_name
        self.language = language
        self.engine = None
        
    def run(self):
        total_files = len(self.audio_paths)
        successful_files = []
        failed_files = []
        
        try:
            self.progress.emit("Initializing transcription engine...")
            self.engine = TranscriptionEngine(model_name=self.model_name)
            
            for idx, audio_path in enumerate(self.audio_paths, 1):
                try:
                    self.progress.emit("=" * 60)
                    self.progress.emit(f"Processing file {idx} of {total_files}")
                    self.progress.emit(f"File: {os.path.basename(audio_path)}")
                    self.progress.emit("=" * 60)
                    
                    self.progress.emit("Loading audio file...")
                    
                    self.progress.emit("Transcribing audio (this may take a while)...")
                    captions = self.engine.transcribe_audio(audio_path, language=self.language)
                    
                    # Auto-save JSON file in same directory with same name
                    output_path = Path(audio_path).with_suffix('.json')
                    self.progress.emit(f"Saving captions to: {output_path.name}")
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(captions, f, indent=2, ensure_ascii=False)
                    
                    self.progress.emit(f"✓ Successfully generated {len(captions)} caption segments!")
                    self.progress.emit(f"✓ Saved to: {output_path}")
                    successful_files.append(os.path.basename(audio_path))
                    self.file_completed.emit(idx, total_files, os.path.basename(audio_path))
                    
                except Exception as e:
                    error_msg = f"✗ Error processing {os.path.basename(audio_path)}: {str(e)}"
                    self.progress.emit(error_msg)
                    failed_files.append(os.path.basename(audio_path))
            
            # Final summary
            self.progress.emit("")
            self.progress.emit("=" * 60)
            self.progress.emit("BATCH PROCESSING COMPLETED")
            self.progress.emit("=" * 60)
            self.progress.emit(f"Total files: {total_files}")
            self.progress.emit(f"Successful: {len(successful_files)}")
            self.progress.emit(f"Failed: {len(failed_files)}")
            
            if successful_files:
                self.progress.emit("\nSuccessfully processed:")
                for filename in successful_files:
                    self.progress.emit(f"  ✓ {filename}")
            
            if failed_files:
                self.progress.emit("\nFailed to process:")
                for filename in failed_files:
                    self.progress.emit(f"  ✗ {filename}")
            
            success = len(failed_files) == 0
            summary = f"{len(successful_files)}/{total_files} files processed successfully"
            self.finished.emit(success, summary)
            
        except Exception as e:
            error_msg = f"Error during batch transcription: {str(e)}"
            self.progress.emit(error_msg)
            self.finished.emit(False, error_msg)


class VoxaCaptionsApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.audio_paths = []  # Changed to list for batch processing
        self.transcription_thread = None
        
        # Check and download models if needed
        self.ensure_models_available()
        
        self.init_ui()
    
    def ensure_models_available(self):
        """Ensure required models are downloaded before app starts"""
        # Determine base directory (handles both dev and bundled exe)
        if getattr(sys, 'frozen', False):
            # Running as bundled exe (PyInstaller --onedir)
            # Models are in _internal folder with --add-data
            if hasattr(sys, '_MEIPASS'):
                base_dir = Path(sys._MEIPASS)
            else:
                base_dir = Path(sys.executable).parent / "_internal"
        else:
            # Running as script - models in script directory
            base_dir = Path(__file__).parent
        
        models_dir = base_dir / "models"
        main_exe = models_dir / "main.exe"
        
        # Check if at least one model exists
        has_models = False
        if models_dir.exists():
            has_models = any(models_dir.glob("ggml-*.bin"))
        
        if not has_models or not main_exe.exists():
            # If running as bundled exe and models not found, this is an error
            if getattr(sys, 'frozen', False):
                QMessageBox.critical(
                    None,
                    "Models Not Found",
                    f"This application was not built correctly.\n\n"
                    f"Models directory: {models_dir}\n"
                    f"Directory exists: {models_dir.exists()}\n"
                    f"Has model files: {has_models}\n"
                    f"main.exe exists: {main_exe.exists()}\n\n"
                    f"Please rebuild using: build.ps1"
                )
                sys.exit(1)
            else:
                # Running as script - offer to download
                self._download_models_script()
    
    def _get_available_models(self):
        """Detect which models are actually available"""
        # Determine base directory
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                base_dir = Path(sys._MEIPASS)
            else:
                base_dir = Path(sys.executable).parent / "_internal"
        else:
            base_dir = Path(__file__).parent
        
        models_dir = base_dir / "models"
        
        if not models_dir.exists():
            return []
        
        # Model info: (filename, display_name)
        all_models = [
            ("ggml-tiny.bin", "tiny (75 MB, fastest, lowest quality)"),
            ("ggml-base.bin", "base (142 MB, fast, good quality)"),
            ("ggml-small.bin", "small (466 MB, balanced) ✓"),
            ("ggml-medium.bin", "medium (1.5 GB, slower, better quality)"),
            ("ggml-large-v3.bin", "large-v3 (2.9 GB, slowest, best quality)")
        ]
        
        available = []
        for filename, display_name in all_models:
            if (models_dir / filename).exists():
                available.append(display_name)
        
        return available
    
    def _download_models_script(self):
        
        # If running as script, offer to download
        reply = QMessageBox.question(
            None,
            "First Time Setup",
            "Voxa-Captions needs to download required models for offline transcription.\n\n"
            "This is a one-time download (~500 MB) and requires internet connection.\n"
            "After this, the app will work completely offline.\n\n"
            "Download now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.No:
            QMessageBox.critical(
                None,
                "Cannot Continue",
                "Models are required to run the application.\n"
                "Please run 'setup_models.py' manually or restart the app."
            )
            sys.exit(1)
        
        # Download models
        progress_dialog = QMessageBox(None)
        progress_dialog.setWindowTitle("Downloading Models")
        progress_dialog.setText("Downloading Whisper models and binaries...\n\n"
                               "This may take several minutes depending on your connection.\n"
                               "Please wait...")
        progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Run setup_models.py
            setup_script = Path(__file__).parent / "setup_models.py"
            result = subprocess.run(
                [sys.executable, str(setup_script)],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            progress_dialog.close()
            
            if result.returncode == 0:
                QMessageBox.information(
                    None,
                    "Setup Complete",
                    "Models downloaded successfully!\n\n"
                    "Voxa-Captions is now ready to use offline."
                )
            else:
                QMessageBox.critical(
                    None,
                    "Download Failed",
                    f"Failed to download models:\n\n{result.stderr}\n\n"
                    "Please check your internet connection and try again."
                )
                sys.exit(1)
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(
                None,
                "Error",
                f"An error occurred during setup:\n\n{str(e)}\n\n"
                "Please run 'setup_models.py' manually."
            )
            sys.exit(1)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Voxa-Captions - Offline Audio Caption Generator")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Voxa-Captions")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Generate captions from audio files - Works 100% offline")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(subtitle_label)
        
        # Audio file selection
        file_group = QGroupBox("Audio Files")
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel("No files selected")
        self.file_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        file_layout.addWidget(self.file_label)
        
        self.browse_button = QPushButton("Browse Audio Files (Multiple Selection)")
        self.browse_button.setMinimumHeight(40)
        self.browse_button.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(self.browse_button)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Model selection
        settings_group = QGroupBox("Transcription Settings")
        settings_layout = QVBoxLayout()
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Whisper Model:"))
        self.model_combo = QComboBox()
        
        # Detect available models
        available_models = self._get_available_models()
        if available_models:
            for model_info in available_models:
                self.model_combo.addItem(model_info)
        else:
            # Fallback - show all models
            self.model_combo.addItems([
                "tiny (75 MB, fastest, lowest quality)",
                "base (142 MB, fast, good quality)",
                "small (466 MB, balanced)",
                "medium (1.5 GB, slower, better quality)",
                "large-v3 (2.9 GB, slowest, best quality)"
            ])
        
        model_layout.addWidget(self.model_combo)
        settings_layout.addLayout(model_layout)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "auto (Auto-detect)",
            "en (English)",
            "es (Spanish)",
            "fr (French)",
            "de (German)",
            "it (Italian)",
            "pt (Portuguese)",
            "ru (Russian)",
            "ja (Japanese)",
            "ko (Korean)",
            "zh (Chinese)",
            "ar (Arabic)",
            "hi (Hindi)"
        ])
        self.language_combo.setCurrentIndex(0)  # Default to auto-detect
        lang_layout.addWidget(self.language_combo)
        settings_layout.addLayout(lang_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Generate button
        self.generate_button = QPushButton("Generate Captions")
        self.generate_button.setMinimumHeight(50)
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_button.clicked.connect(self.generate_captions)
        main_layout.addWidget(self.generate_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        main_layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace;")
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Initial log message
        self.log("Welcome to Voxa-Captions!")
        self.log("Select one or multiple audio files to get started.")
        self.log("Files will be processed one after another and saved automatically.")
        
    def log(self, message):
        """Add a message to the log output"""
        self.log_text.append(f"[INFO] {message}")
        
    def browse_audio_file(self):
        """Open file dialog to select multiple audio files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files (Multiple Selection Allowed)",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma);;All Files (*.*)"
        )
        
        if file_paths:
            self.audio_paths = file_paths
            num_files = len(file_paths)
            
            if num_files == 1:
                self.file_label.setText(f"Selected: {os.path.basename(file_paths[0])}")
                self.log(f"Audio file selected: {os.path.basename(file_paths[0])}")
            else:
                self.file_label.setText(f"Selected {num_files} files")
                self.log(f"{num_files} audio files selected:")
                for file_path in file_paths:
                    self.log(f"  • {os.path.basename(file_path)}")
            
            self.generate_button.setEnabled(True)
            
    def get_model_name(self):
        """Extract model name from combo box selection"""
        model_text = self.model_combo.currentText()
        return model_text.split()[0]  # Extract first word (model name)
    
    def get_language(self):
        """Extract language code from combo box selection"""
        lang_text = self.language_combo.currentText()
        return lang_text.split()[0]  # Extract first word (language code)
    
    def generate_captions(self):
        """Start the caption generation process"""
        if not self.audio_paths:
            QMessageBox.warning(self, "No Files", "Please select audio files first.")
            return
        
        model_name = self.get_model_name()
        language = self.get_language()
        
        # Check if model exists
        models_dir = Path(__file__).parent / "models"
        model_file = models_dir / f"ggml-{model_name}.bin"
        
        if not model_file.exists():
            reply = QMessageBox.question(
                self,
                "Model Not Found",
                f"The selected model '{model_name}' is not downloaded.\n\n"
                f"Would you like to download it now?\n"
                f"(You can also run 'download_models.py' manually)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QMessageBox.information(
                    self,
                    "Download Required",
                    "Please run 'download_models.py' to download the required models.\n"
                    "The app will continue once models are downloaded."
                )
            return
        
        # Disable UI during transcription
        self.browse_button.setEnabled(False)
        self.generate_button.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.language_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.log_text.clear()
        
        num_files = len(self.audio_paths)
        self.log(f"Starting batch transcription of {num_files} file(s)")
        self.log(f"Model: {model_name}")
        self.log(f"Language: {language}")
        self.log("Files will be processed one after another...")
        self.log("Each file will be auto-saved in its original directory.")
        self.log("")
        
        # Start transcription in background thread
        self.transcription_thread = TranscriptionThread(
            self.audio_paths,
            model_name,
            language
        )
        self.transcription_thread.progress.connect(self.log)
        self.transcription_thread.finished.connect(self.on_transcription_finished)
        self.transcription_thread.start()
        
    def on_transcription_finished(self, success, message):
        """Handle transcription completion"""
        # Re-enable UI
        self.browse_button.setEnabled(True)
        self.generate_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.language_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                "Batch Processing Complete",
                f"Caption generation finished!\n\n{message}\n\n"
                f"All files have been saved in their original directories with .json extension."
            )
        else:
            QMessageBox.warning(
                self,
                "Batch Processing Completed with Errors",
                f"Some files may have failed:\n\n{message}\n\n"
                f"Check the log for details."
            )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = VoxaCaptionsApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
