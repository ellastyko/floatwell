from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .panels import PreviewPanel, SettingsPanel, ControlPanel
from PyQt5.QtWidgets import (QDockWidget, QToolBox, QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from qt.widgets.components.buttons import PushButton
from qt.widgets.components.inputs import create_labeled_combobox
from qt.style import StyleManager

class SidebarDock(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(450)
        
        # Основные настройки стиля
        self.setStyleSheet(StyleManager.get_style("QDockWidget"))
        # Создаем контейнерный виджет
        container = QWidget()
        self.setWidget(container)
        
        # Основной layout для контейнера
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # self.toolbox = QToolBox()
        # self.toolbox.setStyleSheet(StyleManager.get_style("QToolBox"))
        # self.layout.addWidget(self.toolbox)
        
        # Добавляем разделы в ToolBox
        self._add_sections()
        
        # Добавляем растягивающийся элемент внизу
        self.layout.addStretch()

        controller = ControlPanel()
        self.layout.addWidget(controller)

    def _add_sections(self):
        """Добавляем разделы в ToolBox"""
        
        # --- Settings (ProxiesPanel) ---
        # settings_widget = PreviewPanel()
        # settings_widget.setStyleSheet(
        #     'background-color: #212327; border-radius: 0 0 5px 5px;'
        # )

        # --- Controller (ControlPanel) ---
        settings_widget = SettingsPanel()
        # settings_widget.setStyleSheet("background-color: #212327;")

        # self.layout.addWidget(settings_widget)
        self.layout.addWidget(settings_widget)

