from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .panels import ControlPanel, NotificationsPanel
from PyQt5.QtWidgets import (QDockWidget, QToolBox, QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from qt.widgets.components.buttons import PushButton
from qt.widgets.components.inputs import create_labeled_combobox
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QPropertyAnimation, Qt

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        # NOT EXPANDED ACTIVE BY DEFAULT
        self.expanded = False
        self.setFixedWidth(60)

        self.setAttribute(Qt.WA_StyledBackground, True) 
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        # --- Control panel всегда снизу ---
        self.notifications_panel = NotificationsPanel()
        self.control_panel = ControlPanel()
        self.layout.addWidget(self.notifications_panel)
        self.layout.addStretch()
        self.layout.addWidget(self.control_panel)

    def toggle(self):
        start = self.width()
        end = 60 if self.expanded else 260
        self.expanded = not self.expanded

        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(220)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()
