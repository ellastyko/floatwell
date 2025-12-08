from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedLayout

from .applogs import LogWidget
from .tables import ItemsTableWidget
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

        layout.addWidget(self.nav)
        layout.addLayout(self.view_stack, stretch=10)

        self.market = None
        self.logs  = None

        ui.mode.connect(self.mode_changed)

        # Default view
        self.show_market()
    
    def mode_changed(self, mode):
        if mode == 'market':
            self.show_market()
        if mode == 'logs':
            self.show_logs()

    def show_logs(self):
        if self.market:
            self.view_stack.removeWidget(self.market)
            self.market.deleteLater()
            self.market = None
        
        if self.logs is None:
            self.logs = LogWidget()
            self.view_stack.addWidget(self.logs)

        self.view_stack.setCurrentWidget(self.logs)

    def show_market(self):
        if self.logs:
            self.view_stack.removeWidget(self.logs)
            self.logs.deleteLater()
            self.logs = None

        if self.market is None:
            self.market = ItemsTableWidget()
            self.view_stack.addWidget(self.market)

        self.view_stack.setCurrentWidget(self.market)

    def closeEvent(self, event):
        if self.market:
            self.market.closeEvent(event)
        event.accept()