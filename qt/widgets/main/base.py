from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedLayout
from qt.widgets.main.tabs.applogs import LogWidget
from .tabs.listings import ListingsTabWidget
from .tabs.proxies import ProxiesTabWidget
from .tabs.steam import SteamTabWidget
from .tabs.settings import SettingsTabWidget
from qt.signals import ui

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.view_stack = QStackedLayout()
        layout.addLayout(self.view_stack)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.listings = ListingsTabWidget()
        self.proxies  = ProxiesTabWidget()  
        self.logs     = LogWidget()
        self.steam    = SteamTabWidget()
        self.settings = SettingsTabWidget()

        self.view_stack.addWidget(self.listings)
        self.view_stack.addWidget(self.proxies)
        self.view_stack.addWidget(self.logs)
        self.view_stack.addWidget(self.steam)
        self.view_stack.addWidget(self.settings)

        ui.mode.connect(self.mode_changed)

        # Default view
        self.view_stack.setCurrentWidget(self.listings)
    
    def mode_changed(self, mode):
        if mode == 'listings':
            self.view_stack.setCurrentWidget(self.listings)
        elif mode == 'logs':
            self.view_stack.setCurrentWidget(self.logs)
        elif mode == 'proxies':
            self.view_stack.setCurrentWidget(self.proxies)
        elif mode == 'steam':
            self.view_stack.setCurrentWidget(self.steam)
        elif mode == 'settings':
            self.view_stack.setCurrentWidget(self.settings)
