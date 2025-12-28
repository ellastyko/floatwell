from PyQt5.QtWidgets import (QWidget, QTableWidget, QHeaderView, QGroupBox, QVBoxLayout, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import webbrowser
from qt.style import StyleManager
from qt.widgets.main.tables import ItemsTableWidget

class ListingsTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)  
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("ListingsTab")
        self.setStyleSheet("""
            #ListingsTab {
                background-color: #1e1e1e;
                border: 1px solid #444;
                color: #f8faff;
            }
        """)

        table_wrapper = ItemsTableWidget()
        layout.addWidget(table_wrapper)
