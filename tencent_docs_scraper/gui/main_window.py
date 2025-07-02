# gui/main_window.py
import sys
import asyncio
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableView, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import QThread, QObject, Signal

# 假设PandasModel和extractor已在其他文件中定义
from .data_model import PandasModel
from core.extractor import fetch_sheet_data
from core.authenticator import initial_authentication

class Worker(QObject):
    finished = Signal(object)  # 信号，完成后发射DataFrame
    error = Signal(str)

    def __init__(self, url, auth_file):
        super().__init__()
        self.url = url
        self.auth_file = auth_file

    def run(self):
        try:
            # 在新线程中运行asyncio事件循环
            df = asyncio.run(fetch_sheet_data(self.url, self.auth_file))
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))

class AuthWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, auth_file):
        super().__init__()
        self.auth_file = auth_file

    def run(self):
        try:
            asyncio.run(initial_authentication(self.auth_file))
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tencent Docs Scraper")
        self.setup_ui()
        self.thread = None
        self.worker = None
        self.auth_file = "auth_state.json"
        self.check_auth_state()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Ready.")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Tencent Sheet URL here...")
        self.fetch_button = QPushButton("Fetch Data")
        self.auth_button = QPushButton("Run First-Time Authentication")
        self.table_view = QTableView()

        layout.addWidget(self.status_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.auth_button)
        layout.addWidget(self.table_view)

        self.fetch_button.clicked.connect(self.start_fetching)
        self.auth_button.clicked.connect(self.start_authentication)

    def check_auth_state(self):
        if not os.path.exists(self.auth_file):
            self.status_label.setText("Authentication file not found. Please run first-time auth.")
            self.fetch_button.setEnabled(False)
        else:
            self.status_label.setText("Ready. Enter URL and click Fetch.")
            self.fetch_button.setEnabled(True)

    def start_authentication(self):
        self.auth_button.setEnabled(False)
        self.status_label.setText("Authentication process started in a new browser...")

        self.thread = QThread()
        self.auth_worker = AuthWorker(self.auth_file)
        self.auth_worker.moveToThread(self.thread)

        self.thread.started.connect(self.auth_worker.run)
        self.auth_worker.finished.connect(self.on_auth_finished)
        self.auth_worker.error.connect(self.on_error)
        self.auth_worker.finished.connect(self.thread.quit)
        self.auth_worker.finished.connect(self.auth_worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_auth_finished(self):
        self.status_label.setText("Authentication successful! You can now fetch data.")
        self.auth_button.setEnabled(True)
        self.check_auth_state()


    def start_fetching(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL.")
            return

        self.fetch_button.setEnabled(False)
        self.status_label.setText("Fetching data... please wait.")

        self.thread = QThread()
        self.worker = Worker(url, self.auth_file)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_data)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def display_data(self, df):
        if df is not None and not df.empty:
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.status_label.setText(f"Success! Displaying {len(df)} rows.")
        else:
            self.status_label.setText("Failed to fetch data or data is empty.")
        self.fetch_button.setEnabled(True)

    def on_error(self, err_msg):
        self.status_label.setText(f"Error: {err_msg}")
        self.fetch_button.setEnabled(True)
        self.auth_button.setEnabled(True)
