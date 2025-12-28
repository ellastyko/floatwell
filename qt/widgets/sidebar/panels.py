from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .styles import *
from qt.widgets.components.buttons import PushButton
from qt.controllers import parser
from qt.widgets.components.buttons import SidebarButton
from utils.helpers import resource_path
from qt.tools import colorize_icon

class PreviewPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
            border-radius: 5px;
            color: white;
        """)

        # Создаем заголовок
        self.label_title = QLabel("Preview")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
            margin-bottom: 10px;
        """)

        layout.addWidget(self.label_title)

        layout.addStretch()

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.setup_buttons()

    def setup_buttons(self):
        start_icon = colorize_icon(resource_path("assets/images/navigation/play.svg"), '#3AC569')
        stop_icon = colorize_icon(resource_path("assets/images/navigation/stop.svg"), '#FF5F57')

        self.run_btn   = SidebarButton(icon=start_icon, tooltip="Start synchronization", label="Run parsing")
        self.pause_btn = SidebarButton(icon=stop_icon, tooltip="Stop synchronization", label="Pause")
        self.pause_btn.setDisabled(True)

        self.run_btn.set_expanded(False)  # сжатый вид
        self.pause_btn.set_expanded(False)  # сжатый вид

        self.run_btn.clicked.connect(self.on_run)
        self.pause_btn.clicked.connect(self.on_pause)
        parser.stopped.connect(self.on_worker_finished)

        self.layout.addWidget(self.run_btn)
        self.layout.addWidget(self.pause_btn)
    
    # Control buttons
    def on_worker_finished(self):
        self.run_btn.setEnabled(True) 
        self.pause_btn.setDisabled(True)

    def on_run(self):
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        parser.start()  # запускаем парсер
        
    def on_pause(self):        
        parser.stop()
        