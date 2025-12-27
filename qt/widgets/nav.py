from PyQt5.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from qt.signals import ui
from qt.widgets.components.buttons import NavButton
from utils.helpers import resource_path
from qt.tools import colorize_icon

class NavWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 40, 8, 8)  # увеличенный верхний отступ
        layout.setSpacing(10)  # расстояние между кнопками

        self.setFixedWidth(60)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.setLayout(layout)

        # Основные кнопки с иконками
        # Укажи путь к своим .png/.svg или используем QIcon.fromTheme
        buttons = [
            ("Listings", colorize_icon(resource_path("assets/images/navigation/listings.svg"), '#fff'), lambda: ui.mode.emit('listings')),
            ("Logs",     colorize_icon(resource_path("assets/images/navigation/logs.svg"), '#fff'), lambda: ui.mode.emit('logs')),
            ("Proxies",  colorize_icon(resource_path("assets/images/navigation/proxies.svg"), '#fff'),  lambda: ui.mode.emit('proxies')),
            # ("Autobuy",  colorize_icon(resource_path("assets/images/navigation/listings.svg"), '#fff'),  lambda: ui.mode.emit('autobuy')),
        ]

        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        for i, (name, icon_path, callback) in enumerate(buttons):
            btn = NavButton(icon=QIcon(icon_path), tooltip=name)
            btn.setCheckable(True)
            btn.clicked.connect(callback)

            self.mode_button_group.addButton(btn, i)
            layout.addWidget(btn)

        layout.addStretch()  # чтобы кнопки прижались к верху
