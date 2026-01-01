from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PyQt5.QtCore import Qt
from core.controllers import parser
from qt.widgets.components.buttons import SidebarButton
from utils.helpers import resource_path
from qt.tools import colorize_icon
from core.telegram.bot import bot
from core.settings import settings_manager

class NotificationsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(6, 20, 6, 20)
        self.setup_buttons()

    def setup_buttons(self):
        start_icon = resource_path("assets/images/navigation/windows.svg")
        stop_icon = resource_path("assets/images/navigation/telegram.svg")

        self.run_btn   = SidebarButton(icon_path=start_icon, tooltip="Enable desktop notifications")
        self.pause_btn = SidebarButton(icon_path=stop_icon, tooltip="Enable telegram notifications")
        self.pause_btn.setDisabled(True)

        self.run_btn.clicked.connect(self.enable_desktop_notifications)
        self.pause_btn.clicked.connect(self.enable_telegram_notifications)

        self.layout.addWidget(self.run_btn)
        self.layout.addWidget(self.pause_btn)

    def enable_desktop_notifications(self):
        settings_manager.get('notifications.telegram')

    def enable_telegram_notifications(self):
        is_enabled = settings_manager.get('notifications.telegram', False)

        if is_enabled:
            bot.stop()
            settings_manager.set('notifications.telegram', False)
        else:
            settings_manager.set('notifications.telegram', True)
            bot.start()

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(6, 20, 6, 20)
        self.setup_buttons()

    def setup_buttons(self):
        start_icon = colorize_icon(resource_path("assets/images/navigation/play.svg"), '#3AC569')
        stop_icon = colorize_icon(resource_path("assets/images/navigation/stop.svg"), '#FF5F57')

        self.run_btn   = SidebarButton(icon_path=start_icon, tooltip="Start synchronization")
        self.pause_btn = SidebarButton(icon_path=stop_icon, tooltip="Stop synchronization")
        self.pause_btn.setDisabled(True)

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
        from PyQt5.QtWidgets import QApplication

        self.pause_btn.setDisabled(True)
        QApplication.processEvents()
        parser.stop()
        