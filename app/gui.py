import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import QThread, Signal

# File Paths
PACKET_CAPTURE_SCRIPT = "app/packet_capture.py"
TRAIN_MODEL_SCRIPT = r"train_model.py"
IDS_SCRIPT = "ids.py"

# Thread class to run commands and capture output
class CommandThread(QThread):
    output_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None  # Store process instance

    def run(self):
        """Execute command and capture stdout."""
        self.process = subprocess.Popen(
            ["python", self.command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in self.process.stdout:
            self.output_signal.emit(line.strip())

        self.process.wait()
        self.finished_signal.emit()

    def stop(self):
        """Terminate the running process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.finished_signal.emit()

# Main GUI Window
class BigDefendGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Window Properties
        self.setWindowTitle("Big Defend - Intrusion Detection System")
        self.setGeometry(100, 100, 600, 500)

        # Title Label with Cool Font
        self.title_label = QLabel("Big Defend")
        self.title_label.setFont(QFont("Arial Black", 18))

        # Console Log TextArea
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setFont(QFont("Courier", 10))

        # Buttons
        self.btn_capture = QPushButton("Start Packet Capture")
        self.btn_train = QPushButton("Train Model")
        self.btn_start_ids = QPushButton("Start IDS")
        self.btn_stop_ids = QPushButton("Stop IDS")
        
        # Set Default Visibility
        self.btn_stop_ids.setVisible(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.btn_capture)
        layout.addWidget(self.btn_train)
        layout.addWidget(self.btn_start_ids)
        layout.addWidget(self.btn_stop_ids)
        layout.addWidget(self.console_log)

        self.setLayout(layout)

        # Button Actions
        self.btn_capture.clicked.connect(lambda: self.run_command(PACKET_CAPTURE_SCRIPT))
        self.btn_train.clicked.connect(lambda: self.run_command(TRAIN_MODEL_SCRIPT))
        self.btn_start_ids.clicked.connect(self.start_ids)
        self.btn_stop_ids.clicked.connect(self.stop_ids)

        self.current_thread = None  # Store running thread

    def run_command(self, script_name):
        """Run a script and show output in console."""
        if self.current_thread and self.current_thread.isRunning():
            self.console_log.append("⚠️ Please stop the running process first!")
            return

        self.console_log.append(f"▶ Running: {script_name}...\n")
        self.current_thread = CommandThread(script_name)
        self.current_thread.output_signal.connect(self.console_log.append)
        self.current_thread.start()

    def start_ids(self):
        """Start IDS and hide other buttons."""
        self.run_command(IDS_SCRIPT)
        self.btn_capture.setVisible(False)
        self.btn_train.setVisible(False)
        self.btn_start_ids.setVisible(False)
        self.btn_stop_ids.setVisible(True)

    def stop_ids(self):
        """Stop IDS and show other buttons again."""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop()
            self.console_log.append("⛔ IDS Stopped.\n")

        self.btn_capture.setVisible(True)
        self.btn_train.setVisible(True)
        self.btn_start_ids.setVisible(True)
        self.btn_stop_ids.setVisible(False)

# Run GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BigDefendGUI()
    window.show()
    sys.exit(app.exec())
