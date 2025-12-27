from PyQt5.QtWidgets import QPushButton
from qt.style import StyleManager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class PushButton(QPushButton):
    def __init__(self, text = None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.__init_ui()

    def __init_ui(self):
        self.setStyleSheet(StyleManager.get_style("QPushButton"))

class NavButton(QPushButton):
    def __init__(self, icon=None, tooltip=None):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(icon if icon else QIcon())
        self.setIconSize(QSize(22, 22))  # размер иконки
        if tooltip:
            self.setToolTip(tooltip)
        self.__init_ui()

    def __init_ui(self):
        self.setFixedHeight(44)
        self.setFixedWidth(44)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2F3136;   /* базовый фон sidebar */
                border: none;
                border-radius: 12px;         /* круглые края */
            }

            QPushButton:hover {
                background-color: #3A3C43;   /* чуть светлее при наведении */
            }

            QPushButton:pressed {
                background-color: #232427;   /* темнее при нажатии */
            }

            QPushButton:checked {
                background-color: #5865F2;   /* Discord-синий для активного */
            }

            QPushButton:disabled {
                background-color: #2F3136;
                color: #777;
            }
        """)
