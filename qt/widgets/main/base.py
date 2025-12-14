from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedLayout

from .applogs import LogWidget
from .tables import ItemsTableWidget, ProxiesTableWidget
from .nav import NavWidget
from qt.signals import ui

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.nav = NavWidget(self)
        self.view_stack = QStackedLayout()

        layout.addWidget(self.nav, stretch=1)
        layout.addLayout(self.view_stack, stretch=10)

        self.market  = ItemsTableWidget()
        self.proxies = ProxiesTableWidget()  
        self.logs    = LogWidget()

        self.view_stack.addWidget(self.market)
        self.view_stack.addWidget(self.proxies)
        self.view_stack.addWidget(self.logs)

        ui.mode.connect(self.mode_changed)

        # Default view
        self.view_stack.setCurrentWidget(self.market)
    
    def mode_changed(self, mode):
        if mode == 'listings':
            self.view_stack.setCurrentWidget(self.market)
        elif mode == 'logs':
            self.view_stack.setCurrentWidget(self.logs)
        elif mode == 'proxies':
            self.view_stack.setCurrentWidget(self.proxies)

    def closeEvent(self, event):
        if self.market:
            self.market.closeEvent(event)
        event.accept()

    def closeEvent(self, event):
        if self.market:
            self.market.closeEvent(event)
        event.accept()