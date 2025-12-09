from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .panels import ProxiesPanel, ControlPanel
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
        layout = QVBoxLayout(container)
        
        self.toolbox = QToolBox()
        self.toolbox.setStyleSheet(StyleManager.get_style("QToolBox"))
        layout.addWidget(self.toolbox)
        
        # Добавляем разделы в ToolBox
        self._add_sections()
        
        # Добавляем растягивающийся элемент внизу
        layout.addStretch()

    def _add_sections(self):
        """Добавляем разделы в ToolBox"""
        
        # --- Settings (ProxiesPanel) ---
        self.settings_widget = ProxiesPanel()
        self.settings_widget.setStyleSheet(
            'background-color: #212327; border-radius: 0 0 5px 5px;'
        )

        # Кладём виджет напрямую, ЛЭЙАУТ НЕ МЕНЯЕМ
        # self.toolbox.addItem(self.settings_widget, "Settings")

        # --- Controller (ControlPanel) ---
        controller_widget = ControlPanel()
        controller_widget.setStyleSheet("background-color: #212327;")

        self.toolbox.addItem(controller_widget, "Controller")

