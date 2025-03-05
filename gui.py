import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QLabel, QSizePolicy, QProgressBar, QMessageBox
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QPalette, QColor

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Execution Dashboard")
        self.resize(800, 600)
        self.processes = {}  # key: process, value: script name

        # Define the base directory for scripts.
        # Update this to match your file structure.
        self.script_dir = os.path.join(os.getcwd(), "scripts")

        # Apply modern Fusion style and custom dark palette.
        self.setup_style()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Status label and progress bar
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress by default
        self.progress_bar.hide()

        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)

        # Instruction label
        label = QLabel("Click a button to execute the corresponding script:")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(label)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.ids_btn = QPushButton("Run IDS")
        self.packet_btn = QPushButton("Run Packet Capture")
        self.train_btn = QPushButton("Train Model")
        self.stop_btn = QPushButton("Stop Process")
        self.clear_btn = QPushButton("Clear Console")

        # Set style sheets for buttons
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """
        for btn in [self.ids_btn, self.packet_btn, self.train_btn, self.stop_btn, self.clear_btn]:
            btn.setStyleSheet(button_style)
            btn.setMinimumWidth(120)
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)

        # Console output widget
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #dcdcdc;
                border: 1px solid #3e3e3e;
                border-radius: 5px;
                padding: 5px;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
        """)
        self.console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.console)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect buttons to actions
        self.ids_btn.clicked.connect(lambda: self.run_script("ids.py"))
        self.packet_btn.clicked.connect(lambda: self.run_script("packet_capture.py"))
        self.train_btn.clicked.connect(lambda: self.run_script("train_model.py"))
        self.stop_btn.clicked.connect(self.stop_current_process)
        self.clear_btn.clicked.connect(self.console.clear)

        # Variable to track current running process (if only one at a time is allowed)
        self.current_process = None

    def setup_style(self):
        """Set Fusion style and configure a dark palette."""
        app = QApplication.instance()
        app.setStyle("Fusion")

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)

    def run_script(self, script_name):
        """
        Executes the given script in a subprocess and captures its output.
        """
        # Construct full script path using the script directory.
        script_path = os.path.join(self.script_dir, script_name)
        if not os.path.exists(script_path):
            self.append_console(f"❌ Script not found: {script_path}\n")
            return

        # Create and configure QProcess
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.MergedChannels)

        # Connect signals to capture output and status
        process.readyReadStandardOutput.connect(lambda proc=process: self.handle_output(proc))
        process.readyReadStandardError.connect(lambda proc=process: self.handle_output(proc))
        process.started.connect(lambda: self.on_process_started(script_name, process))
        process.finished.connect(lambda exitCode, exitStatus, proc=process: self.on_process_finished(script_name, exitCode, exitStatus, proc))

        # Start the process using the same Python interpreter
        python_executable = sys.executable
        process.start(python_executable, [script_path])

        # Track the current process
        self.current_process = process
        self.processes[process] = script_name

    def on_process_started(self, script_name, process):
        self.append_console(f"🚀 Starting {script_name}...\n")
        self.status_label.setText(f"Running: {script_name}")
        self.progress_bar.show()

    def handle_output(self, process):
        """
        Reads output from the process and appends it to the console.
        """
        output = process.readAllStandardOutput().data().decode("utf-8")
        self.append_console(output)

    def on_process_finished(self, script_name, exitCode, exitStatus, process):
        self.append_console(f"\n✅ {script_name} finished with exit code {exitCode}\n")
        self.status_label.setText("Idle")
        self.progress_bar.hide()
        # Clean up the process reference
        if process in self.processes:
            del self.processes[process]
        if self.current_process == process:
            self.current_process = None

    def stop_current_process(self):
        """
        Stops the currently running process if any.
        """
        if self.current_process is not None:
            self.current_process.kill()
            self.append_console("⛔ Process was terminated by the user.\n")
            self.status_label.setText("Idle")
            self.progress_bar.hide()
            self.current_process = None
        else:
            QMessageBox.information(self, "No Process Running", "There is no active process to stop.")

    def append_console(self, text):
        """
        Append text to the console widget.
        """
        self.console.appendPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
