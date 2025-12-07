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
        
        self.settings_widget  = ProxiesPanel()
        self.control_widget   = ControlPanel()
        
        layout.addWidget(self.settings_widget, stretch=3)
        layout.addWidget(self.control_widget, stretch=2)
        
        
        # Добавляем растягивающийся элемент внизу
        layout.addStretch()

    def _add_sections(self):
        """Добавляем разделы в ToolBox"""
        # Videocapture
        vcapture_section = QWidget()
        vcapture_section.setStyleSheet('background-color: #212327; border-radius: 0 0 5px 5px;')
        vcapture_layout = QVBoxLayout(vcapture_section)

        vcapture_layout.addWidget(PushButton("Start"))
        vcapture_layout.addStretch()
        self.toolbox.addItem(vcapture_section, "Videocapture")
        
        # Settings
        section2 = QWidget()
        section2.setStyleSheet('background-color: #212327;')
        section2_layout = QVBoxLayout(section2)
        section2_layout.addWidget(QLabel("Settings"))
        section2_layout.addWidget(PushButton("Apply"))
        section2_layout.addStretch()
        self.toolbox.addItem(section2, "Settings")

