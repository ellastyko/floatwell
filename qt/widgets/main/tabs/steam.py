from PyQt5.QtWidgets import (QWidget, QVBoxLayout)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from qt.style import StyleManager

class SteamTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)  
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("SteamTab")
        self.setStyleSheet("""
            #SteamTab {
                background-color: #1e1e1e;
                border: 1px solid #444;
                color: #f8faff;
            }
        """)

        
