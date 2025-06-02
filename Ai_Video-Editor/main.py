import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox, QComboBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from utils.audio_analysis import analyze_audio
from utils.video_analysis import detect_motion
from utils.highlight_generator import generate_highlights
from moviepy.editor import VideoFileClip


class HighlightWorker(QThread):
    progress = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_path, bitrate, output_folder):
        super().__init__()
        self.video_path = video_path
        self.bitrate = bitrate
        self.output_folder = output_folder
        self._is_interrupted = False

    def run(self):
        try:
            self.progress.emit("🔍 Extracting audio from video...")
            clip = VideoFileClip(self.video_path)
            audio_path = os.path.join(self.output_folder, "temp_audio.wav")
            clip.audio.write_audiofile(audio_path)
            if self._is_interrupted:
                return

            self.progress.emit("🎵 Analyzing audio for significant moments...")
            audio_times = analyze_audio(audio_path)
            if self._is_interrupted:
                return

            self.progress.emit("🎬 Analyzing the movements in the video....")
            motion_times = detect_motion(self.video_path)
            if self._is_interrupted:
                return

            combined_times = sorted(set(list(audio_times) + motion_times))
            self.progress.emit(f"📌 Total found {len(combined_times)} significant moments.")

            self.progress.emit("⚙️ Generating highlight video...")
            output_path = os.path.join(self.output_folder, "highlight.mp4")
            generate_highlights(self.video_path, combined_times, output_path=output_path, bitrate=self.bitrate)

            if self._is_interrupted:
                return

            self.progress.emit("✅ Završeno!")
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def interrupt(self):
        self._is_interrupted = True


class AIHighlightEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Video Highlight Editor")
        self.setGeometry(200, 200, 460, 320)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: white;
            font-family: Arial;
            font-size: 14px;
            QPushButton {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QComboBox {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 5px;
                color: white;
            }
            QLabel {
                margin: 6px 0px;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #3a3a3a;
            }
            QProgressBar::chunk {
                background-color: #50b050;
                width: 20px;
            }
        """)
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.video_path = ""
        self.output_folder = os.path.abspath("output")
        os.makedirs(self.output_folder, exist_ok=True)

        main_layout = QVBoxLayout()

        self.label = QLabel("Select a video file for analysis:")
        main_layout.addWidget(self.label)

        self.button_select = QPushButton("📁 Choose a video")
        self.button_select.clicked.connect(self.select_video)
        main_layout.addWidget(self.button_select)

        folder_layout = QHBoxLayout()
        self.label_output = QLabel(f"Output folder: {self.output_folder}")
        self.label_output.setWordWrap(True)
        folder_layout.addWidget(self.label_output)

        self.button_select_output = QPushButton("🗂 Choose folder")
        self.button_select_output.clicked.connect(self.select_output_folder)
        folder_layout.addWidget(self.button_select_output)

        main_layout.addLayout(folder_layout)

        self.label_quality = QLabel("Choose the video quality:")
        main_layout.addWidget(self.label_quality)

        self.combo_quality = QComboBox()
        self.combo_quality.addItems([
            "Low (1000k)",
            "Medium (3000k)",
            "High (6000k)"
        ])
        main_layout.addWidget(self.combo_quality)

        self.button_generate = QPushButton("✨ Generate Highlight")
        self.button_generate.clicked.connect(self.process_video)
        self.button_generate.setEnabled(False)
        main_layout.addWidget(self.button_generate)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.result_label = QLabel("")
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)

        self.thread = None

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose a video", "", "Video Files (*.mp4 *.avi *.mov)")
        if path:
            self.video_path = path
            self.label.setText(f"Selected: {os.path.basename(path)}")
            self.button_generate.setEnabled(True)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.label_output.setText(f"Output folder: {self.output_folder}")

    def process_video(self):
        if not self.video_path:
            QMessageBox.warning(self, "Error", "Please select a video file before starting.")
            return

        quality_map = {
            "Low (1000k)": "1000k",
            "Medium (3000k)": "3000k",
            "High (6000k)": "6000k"
        }
        bitrate = quality_map.get(self.combo_quality.currentText(), "3000k")

        self.thread = HighlightWorker(self.video_path, bitrate, self.output_folder)
        self.thread.progress.connect(self.update_status)
        self.thread.finished.connect(self.process_finished)
        self.thread.error.connect(self.process_error)

        self.button_generate.setEnabled(False)
        self.progress_bar.setValue(0)
        self.update_status("Strating processing...")
        self.thread.start()

    def update_status(self, message):
        self.result_label.setText(message)
        # Povezivanje poruka sa progresom (samo primer, možeš dodatno optimizovati)
        mapping = {
            "Extracting the audio from the video...": 10,
            "Analyzing audio for significant moments...": 35,
            "Analyzing the movements in the video....": 60,
            "Total found": 70,
            "Generating highlight video...": 90,
            "Done!": 100,
        }
        for key, val in mapping.items():
            if key in message:
                self.progress_bar.setValue(val)
                break

    def process_finished(self):
        self.progress_bar.setValue(100)
        output_file = os.path.join(self.output_folder, "highlight.mp4")
        self.result_label.setText(f"🎉 Highlight video is ready in '{output_file}'")
        QMessageBox.information(self, "Done", "Highlight is successfully generated!")
        self.button_generate.setEnabled(True)

    def process_error(self, error_msg):
        self.result_label.setText("❌ Došlo je do greške!")
        QMessageBox.critical(self, "Error", f"An error occurred while processing.:\n{error_msg}")
        self.button_generate.setEnabled(True)
        self.progress_bar.setValue(0)

    def closeEvent(self, event):
        # Ako thread radi, prekinuti ga pre zatvaranja
        if self.thread and self.thread.isRunning():
            self.thread.interrupt()
            self.thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIHighlightEditor()
    window.show()
    sys.exit(app.exec_())
