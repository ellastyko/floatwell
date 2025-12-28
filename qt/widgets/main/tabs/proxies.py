from PyQt5.QtWidgets import (QWidget, QVBoxLayout)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from qt.style import StyleManager
from qt.widgets.main.tables import ProxiesTableWidget

class ProxiesTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)  
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("ProxiesTab")
        self.setStyleSheet("""
            #ProxiesTab {
                background-color: #1e1e1e;
                border: 1px solid #444;
                color: #f8faff;
            }
        """)

        table_wrapper = ProxiesTableWidget()
        layout.addWidget(table_wrapper)
