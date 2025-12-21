from PyQt5.QtWidgets import QWidget, QHBoxLayout, QButtonGroup, QSizePolicy
from qt.signals import ui
from qt.widgets.components.buttons import PushButton

class NavWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        self._init_ui()
        
    def _init_ui(self):
        layout = QHBoxLayout()
        # ❗ УБИРАЕМ лишнее пространство
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.setLayout(layout)

        # Основные кнопки режимов
        buttons = [
            ("Listings", lambda: ui.mode.emit('listings')),
            ("Logs", lambda: ui.mode.emit('logs')),
            ("Proxies", lambda: ui.mode.emit('proxies')),
            ("Autobuy", lambda: ui.mode.emit('autobuy')),
        ]

        # Создаем группу для основных кнопок (работают как радио-кнопки)
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        # Добавляем кнопки в группу и layout
        for i, btn_info in enumerate(buttons):
            btn = PushButton(btn_info[0])
            btn.clicked.connect(btn_info[1])
            self.mode_button_group.addButton(btn, i)
            layout.addWidget(btn)

    def _create_mode_button(self, text, mode):
        btn = PushButton(text)
        btn.setCheckable(True)
        btn.mode = mode  # Сохраняем режим как свойство кнопки
        return btn
