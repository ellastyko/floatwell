from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .panels import PreviewPanel, SettingsPanel, ControlPanel
from PyQt5.QtWidgets import (QDockWidget, QToolBox, QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from qt.widgets.components.buttons import PushButton
from qt.widgets.components.inputs import create_labeled_combobox
from qt.style import StyleManager

# class SidebarDock(QDockWidget):
#     def __init__(self, title, parent=None):
#         super().__init__(title, parent)
#         self.setMinimumWidth(200)
#         self.setMaximumWidth(250)
        
#         # Основные настройки стиля
#         self.setStyleSheet(StyleManager.get_style("QDockWidget"))
#         # Создаем контейнерный виджет
#         container = QWidget()
#         self.setWidget(container)
        
#         # Основной layout для контейнера
#         self.layout = QVBoxLayout(container)
#         self.layout.setContentsMargins(0, 0, 0, 0)

#         # Добавляем разделы в ToolBox
#         self._add_sections()
        
#         # Добавляем растягивающийся элемент внизу
#         self.layout.addStretch()

#         controller = ControlPanel()
#         self.layout.addWidget(controller)

#     def _add_sections(self):
#         """Добавляем разделы в ToolBox"""
#         # --- Controller (ControlPanel) ---
#         settings_widget = SettingsPanel()
#         self.layout.addWidget(settings_widget)

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QPropertyAnimation, Qt

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.expanded = True
        self.setFixedWidth(260)

        self.setStyleSheet("""
            background-color: #1e1e1e;
            border-left: 1px solid #333;
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(6)

        # --- Контент ---
        self.settings_panel = SettingsPanel()
        self.layout.addWidget(self.settings_panel)

        self.layout.addStretch()

        # --- Control panel всегда снизу ---
        self.control_panel = ControlPanel()
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

        # Прячем контент при схлопывании
        self.settings_panel.setVisible(self.expanded)
