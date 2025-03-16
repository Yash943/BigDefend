import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QLabel, QSizePolicy, QProgressBar, QMessageBox,
    QFrame, QSpacerItem
)
from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QPalette, QColor, QFont

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Big Defend 🛡️")
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        self.processes = {}  # key: process, value: script name
        self.current_process = None  # Initialize current_process to None

        # Define the base directory for scripts
        self.script_dir = os.path.join(os.getcwd(), "scripts")
        
        # Create scripts directory if it doesn't exist
        if not os.path.exists(self.script_dir):
            os.makedirs(self.script_dir)

        # Apply modern style and custom palette
        self.setup_style()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with logo and title
        header_layout = QHBoxLayout()
        
        # App title
        title_layout = QVBoxLayout()
        app_title = QLabel("Big Defend 🛡️")
        app_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #E0E0E0;
        """)
        
        app_subtitle = QLabel("Hybrid Intrusion Detection System")
        app_subtitle.setStyleSheet("color: #AAAAAA; font-size: 16px;")
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        title_layout.addSpacerItem(QSpacerItem(10, 5))
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #444444;")
        main_layout.addWidget(separator)

        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 44, 52, 0.7);
                border-radius: 8px;
                border: 1px solid #3A3A3A;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        
        status_header = QLabel("System Status")
        status_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        status_header.setAlignment(Qt.AlignCenter)
        
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #8BC34A;
            padding: 5px;
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2D2D30;
                border-radius: 4px;
                height: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4C9EE8;
                border-radius: 4px;
            }
        """)
        self.progress_bar.hide()
        
        status_layout.addWidget(status_header)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(status_frame)

        # Control section with buttons
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 44, 52, 0.7);
                border-radius: 8px;
                border: 1px solid #3A3A3A;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        
        # Control section header
        control_header = QLabel("Security Controls")
        control_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        control_header.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(control_header)
        
        # Button layout with modern buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Create button style function for different colors
        def create_button(text, color, hover_color):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    margin: 1px;
                }}
                QPushButton:disabled {{
                    background-color: #3A3A3A;
                    color: #777777;
                }}
            """)
            btn.setMinimumWidth(150)
            return btn
        
        # Create buttons with different colors
        self.ids_btn = create_button("Run IDS", "#3498DB", "#2980B9")
        self.packet_btn = create_button("Packet Capture", "#2ECC71", "#27AE60") 
        self.train_btn = create_button("Train Model", "#9B59B6", "#8E44AD")
        self.stop_btn = create_button("Stop Process", "#E74C3C", "#C0392B")
        self.clear_btn = create_button("Clear Console", "#7F8C8D", "#95A5A6")
        
        button_layout.addWidget(self.packet_btn)
        button_layout.addWidget(self.train_btn)
        button_layout.addWidget(self.ids_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        
        control_layout.addLayout(button_layout)
        main_layout.addWidget(control_frame)

        # Console output with better styling
        console_frame = QFrame()
        console_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 44, 52, 0.7);
                border-radius: 8px;
                border: 1px solid #3A3A3A;
            }
        """)
        console_layout = QVBoxLayout(console_frame)
        
        console_header = QLabel("System Console")
        console_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        console_header.setAlignment(Qt.AlignCenter)
        
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                selection-background-color: #264F78;
            }
            QScrollBar:vertical {
                border: none;
                background: #2D2D30;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        console_layout.addWidget(console_header)
        console_layout.addWidget(self.console)
        
        main_layout.addWidget(console_frame)

        # Footer with version info
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #777777; font-size: 12px;")
        
        footer_layout.addWidget(version_label)
        main_layout.addLayout(footer_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect buttons to actions
        self.ids_btn.clicked.connect(lambda: self.run_script("ids.py"))
        self.packet_btn.clicked.connect(lambda: self.run_script("packet_capture.py"))
        self.train_btn.clicked.connect(lambda: self.run_script("train_model.py"))
        self.stop_btn.clicked.connect(self.stop_current_process)
        self.clear_btn.clicked.connect(self.console.clear)

        # Initial state of stop button
        self.stop_btn.setEnabled(False)
        
        # Add welcome message to console
        self.append_console("🛡️ Big Defend Hybrid IDS initialized")
        self.append_console("🔒 Ready to monitor and protect your network")
        self.append_console("📊 Select an option to begin...\n")

        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_processes)
        self.cleanup_timer.start(1000)  # Check every second

    def setup_style(self):
        """Set up modern dark theme with gradient"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        # Set modern dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 32, 36))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Link, QColor(66, 155, 248))
        dark_palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        app.setPalette(dark_palette)
        
        # Set application font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Set window style sheet for gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #1A1A2E, stop:1 #16213E);
            }
            QToolTip {
                background-color: #292929;
                color: white;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
        """)

    def run_script(self, script_name):
        """Executes the given script in a subprocess and captures its output."""
        # Check if another process is running
        if self.current_process and self.current_process.state() != QProcess.NotRunning:
            self.append_console("⚠️ Another process is already running")
            return

        # Construct full script path using the script directory
        script_path = os.path.join(self.script_dir, script_name)
        if not os.path.exists(script_path):
            self.append_console(f"❌ Script not found: {script_path}\n")
            return

        # Create and configure QProcess
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.MergedChannels)

        # Connect signals to capture output and status
        process.readyRead.connect(lambda: self.handle_output(process))
        process.started.connect(lambda: self.on_process_started(script_name))
        process.finished.connect(lambda exitCode, exitStatus: 
                               self.on_process_finished(script_name, exitCode, exitStatus))
        process.errorOccurred.connect(lambda error: self.on_process_error(error, script_name))

        # Start the process using the same Python interpreter
        python_executable = sys.executable
        process.start(python_executable, [script_path])

        # Track the current process
        self.current_process = process
        self.processes[process] = script_name

    def on_process_started(self, script_name):
        self.append_console(f"🚀 Starting {script_name}...")
        self.status_label.setText(f"Running: {script_name}")
        self.status_label.setStyleSheet("font-size: 14px; color: #4C9EE8; padding: 5px;")
        self.progress_bar.show()
        self.stop_btn.setEnabled(True)
        
        # Disable other action buttons while process is running
        self.ids_btn.setEnabled(False)
        self.packet_btn.setEnabled(False)
        self.train_btn.setEnabled(False)

    def handle_output(self, process):
        """Reads output from the process and appends it to the console."""
        if process.state() == QProcess.Running:
            output = process.readAll().data().decode("utf-8", errors="replace")
            if output:
                self.append_console(output)

    def on_process_error(self, error, script_name):
        """Handles process errors"""
        error_messages = {
            QProcess.FailedToStart: "The process failed to start.",
            QProcess.Crashed: "The process crashed.",
            QProcess.Timedout: "The process timed out.",
            QProcess.WriteError: "Error writing to the process.",
            QProcess.ReadError: "Error reading from the process.",
            QProcess.UnknownError: "An unknown error occurred."
        }
        
        error_msg = error_messages.get(error, "An unspecified error occurred.")
        self.append_console(f"❌ Error with {script_name}: {error_msg}")
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("font-size: 14px; color: #E74C3C; padding: 5px;")
        self.progress_bar.hide()
        self.stop_btn.setEnabled(False)
        
        # Re-enable action buttons
        self.ids_btn.setEnabled(True)
        self.packet_btn.setEnabled(True)
        self.train_btn.setEnabled(True)

    def on_process_finished(self, script_name, exitCode, exitStatus):
        if exitStatus == QProcess.NormalExit:
            self.append_console(f"✅ {script_name} finished with exit code {exitCode}")
            self.status_label.setText("Idle")
            self.status_label.setStyleSheet("font-size: 14px; color: #8BC34A; padding: 5px;")
        else:
            self.append_console(f"⚠️ {script_name} terminated abnormally with exit code {exitCode}")
            self.status_label.setText("Terminated")
            self.status_label.setStyleSheet("font-size: 14px; color: #FFA726; padding: 5px;")
        
        self.progress_bar.hide()
        self.stop_btn.setEnabled(False)
        
        # Re-enable action buttons
        self.ids_btn.setEnabled(True)
        self.packet_btn.setEnabled(True)
        self.train_btn.setEnabled(True)

    def stop_current_process(self):
        """Stops the currently running process if any."""
        if self.current_process and self.current_process.state() != QProcess.NotRunning:
            script_name = self.processes.get(self.current_process, "Unknown process")
            self.append_console(f"⛔ Terminating {script_name}...")
            
            # Attempt graceful termination first
            self.current_process.terminate()
            
            # Wait a bit for the process to terminate gracefully
            if not self.current_process.waitForFinished(3000):  # 3 seconds timeout
                self.current_process.kill()  # Force kill if it doesn't respond
                self.append_console("⛔ Process was forcefully killed.")
            
            self.status_label.setText("Terminated")
            self.status_label.setStyleSheet("font-size: 14px; color: #FFA726; padding: 5px;")
            self.progress_bar.hide()
            self.stop_btn.setEnabled(False)
            
            # Re-enable action buttons
            self.ids_btn.setEnabled(True)
            self.packet_btn.setEnabled(True)
            self.train_btn.setEnabled(True)
        else:
            QMessageBox.information(self, "No Process Running", "There is no active process to stop.")

    def append_console(self, text):
        """Append text to the console widget with timestamp and scroll to the bottom."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text.rstrip()}"
        self.console.appendPlainText(formatted_text)
        # Ensure the latest output is visible
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def cleanup_processes(self):
        """Clean up finished processes"""
        for process in list(self.processes.keys()):
            if process.state() == QProcess.NotRunning:
                process.deleteLater()
                del self.processes[process]
                if self.current_process == process:
                    self.current_process = None

    def closeEvent(self, event):
        """Handle application close event - terminate any running processes"""
        if self.current_process and self.current_process.state() != QProcess.NotRunning:
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Confirm Exit")
            dialog.setText("A script is still running.")
            dialog.setInformativeText("Are you sure you want to quit?")
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog.setDefaultButton(QMessageBox.No)
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #282C34;
                    color: #E0E0E0;
                }
                QPushButton {
                    background-color: #3A3A3A;
                    color: #E0E0E0;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4A4A4A;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            
            reply = dialog.exec_()
            
            if reply == QMessageBox.Yes:
                # Terminate all running processes
                for process in list(self.processes.keys()):
                    if process.state() != QProcess.NotRunning:
                        process.kill()
                        process.waitForFinished(1000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

        # Stop the cleanup timer
        self.cleanup_timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())