from PyQt5.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QSizePolicy
from qt.signals import ui
from qt.widgets.components.buttons import NavButton
from utils.helpers import resource_path

class NavbarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 40, 0, 40)  # увеличенный верхний отступ
        self.layout.setSpacing(5)  # расстояние между кнопками

        self.setFixedWidth(50)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        # Основные кнопки с иконками
        # Укажи путь к своим .png/.svg или используем QIcon.fromTheme
        topbuttons = [
            ("Listings", resource_path("assets/images/navigation/listings.svg"), lambda: ui.mode.emit('listings')),
            ("Logs",     resource_path("assets/images/navigation/logs.svg"), lambda: ui.mode.emit('logs')),
            ("Proxies",  resource_path("assets/images/navigation/proxies.svg"),  lambda: ui.mode.emit('proxies')),
            # ("Steam",  resource_path("assets/images/navigation/steam.svg"),  lambda: ui.mode.emit('steam')),
        ]

        bottombuttons = [
            ("Settings",  resource_path("assets/images/navigation/settings.svg"),  lambda: ui.mode.emit('settings')),
        ]

        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        self._attach_buttons(topbuttons)

        self.layout.addStretch()  # чтобы кнопки прижались к верху

        self._attach_buttons(bottombuttons)

    def _attach_buttons(self, buttons):
        for i, (name, icon_path, callback) in enumerate(buttons):
            btn = NavButton(icon_path=icon_path, tooltip=name)
            btn.setCheckable(True)
            btn.clicked.connect(callback)

            self.mode_button_group.addButton(btn, i)
            self.layout.addWidget(btn)
