from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PyQt5.QtCore import Qt
from core.controllers import parser
from qt.widgets.components.buttons import SidebarButton, SidebarButtonTheme
from utils.helpers import resource_path
from qt.tools import colorize_icon
# from core.telegram.bot import bot
from core.settings import settings_manager
from qt.signals import applog

class NotificationsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(8, 40, 8, 20)
        self.setup_buttons()

    def setup_buttons(self):
        TG_THEME = SidebarButtonTheme(
            bg_normal="transparent",
            bg_hover="transparent",
            bg_active="transparent",
            icon_normal="#ffffff",
            icon_active="#0088cc",
            icon_size=(30, 30)
        )

        W_THEME = SidebarButtonTheme(
            bg_normal="transparent",
            bg_hover="transparent",
            bg_active="transparent",
            icon_normal="#ffffff",
            icon_active="#0088cc",
            icon_size=(25, 25)
        )

        self.run_btn   = SidebarButton(icon_path=resource_path("assets/images/navigation/windows.svg"), tooltip="Enable desktop notifications", theme=W_THEME, checked=settings_manager.get('notifications.desktop', False))
        self.pause_btn = SidebarButton(icon_path=resource_path("assets/images/navigation/telegram.svg"), tooltip="Enable telegram notifications", theme=TG_THEME, checked=settings_manager.get('notifications.telegram', False))

        self.run_btn.clicked.connect(self.toggle_desktop_notifications)
        self.pause_btn.clicked.connect(self.toggle_telegram_notifications)

        self.layout.addWidget(self.run_btn)
        self.layout.addWidget(self.pause_btn)

    def toggle_desktop_notifications(self):
        is_enabled = settings_manager.get('notifications.desktop', False)
        settings_manager.set('notifications.desktop', not is_enabled)

        msg = 'Windows notifications enabled' if is_enabled else 'Windows notifications enabled'
        applog.log_message.emit(msg, 'warning') 

    def toggle_telegram_notifications(self):
        is_enabled = settings_manager.get('notifications.telegram', False)

        if is_enabled:
            # bot.stop()
            settings_manager.set('notifications.telegram', False)
            applog.log_message.emit('Telegram notifications disabled', 'warning')
        else:
            settings_manager.set('notifications.telegram', True)
            applog.log_message.emit('Telegram notifications enabled', 'warning')
            # bot.start()

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(6, 20, 6, 20)
        self.setup_buttons()

    def setup_buttons(self):
        START_THEME = SidebarButtonTheme(
            bg_normal="transparent",
            bg_hover="transparent",
            bg_active="transparent",
            icon_normal="#3AC569",
            icon_active="#3AC569",
            button_size=(48, 48),
            icon_size=(44, 44),
        )

        STOP_THEME = SidebarButtonTheme(
            bg_normal="transparent",
            bg_hover="transparent",
            bg_active="transparent",
            icon_normal="#FF5F57",
            icon_active="#FF5F57",
            button_size=(48, 48),
            icon_size=(44, 44),
        )

        self.run_btn   = SidebarButton(icon_path=resource_path("assets/images/navigation/play.svg"), tooltip="Start synchronization", theme=START_THEME)
        self.pause_btn = SidebarButton(icon_path=resource_path("assets/images/navigation/stop.svg"), tooltip="Stop synchronization", theme=STOP_THEME)
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
        