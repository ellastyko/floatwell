from PyQt5.QtWidgets import QPushButton
from qt.style import StyleManager

class PushButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.__init_ui()

    def __init_ui(self):
        self.setStyleSheet(StyleManager.get_style("QPushButton"))
    