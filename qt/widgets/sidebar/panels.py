from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .styles import *
from qt.widgets.components.inputs import create_labeled_combobox
from qt.widgets.components.buttons import PushButton

class ProxiesPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
            border-radius: 5px;
            background-color: #303030;
            color: white;
        """)

        # Создаем заголовок
        self.label_title = QLabel("Proxies")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            background-color: #212121; 
            padding: 5px;
            margin-bottom: 10px;
        """)

        layout.addWidget(self.label_title)

        layout.addStretch()

class ControlPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
            border-radius: 5px;
            background-color: #303030;
            color: white;
        """)

        # Создаем заголовок
        self.label_title = QLabel("Controller")
        self.label_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            background-color: #212121; 
            padding: 5px;
            margin-bottom: 10px;
        """)
        self.label_title.setAlignment(Qt.AlignCenter)

        self.run_parsing_btn = PushButton("Run parsing")
        self.restart_btn = PushButton("Restart")
        self.pause_btn = PushButton("Pause")
        self.run_parsing_btn.clicked.connect(self.on_run)
        self.restart_btn.clicked.connect(self.on_restart)
        self.pause_btn.clicked.connect(self.on_pause)

        layout.addWidget(self.label_title, 1)
        layout.addStretch(8)
        layout.addWidget(self.run_parsing_btn)
        layout.addWidget(self.restart_btn)
        layout.addWidget(self.pause_btn)
     
    def on_run(self):
        pass

    def on_restart(self):
        pass

    def on_pause(self):
        pass


        