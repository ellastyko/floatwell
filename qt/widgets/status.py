from PyQt5.QtWidgets import QStatusBar, QWidget, QSizePolicy
from qt.widgets.labels import SessionTime, AppVersionLabel
from PyQt5.QtWidgets import QHBoxLayout
from configurator import config

class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.setSizeGripEnabled(False)
        self.setStyleSheet("""
            QStatusBar {
                padding: 6px;
                background-color: #212327;
            }

            QStatusBar::item {
                background-color: #212327;
                border: none;        /* 🔥 УБИРАЕТ РАЗДЕЛИТЕЛИ */
            }
        """)
        self.setContentsMargins(10, 0, 0, 0)  
        self._set_widgets()

    def _set_widgets(self):
        self.connection_label = SessionTime()
        self.version_label    = AppVersionLabel(config['main']['version'])

        # левый виджет
        self.addWidget(self.connection_label)

        # правый виджет
        self.addPermanentWidget(self.version_label)
