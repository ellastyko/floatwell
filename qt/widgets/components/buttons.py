from PyQt5.QtWidgets import QPushButton
from qt.style import StyleManager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, QEvent
from PyQt5.QtGui import QColor


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
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        if icon:
            self.setIcon(icon)

        self.setIconSize(QSize(24, 24))
        if tooltip:
            self.setToolTip(tooltip)

        self._init_ui()
        self._init_animation()

    def _init_ui(self):
        self.setFixedSize(44, 44)

        self.setStyleSheet("""
            QPushButton {
                background-color: #2F3136;
                border: none;
                border-radius: 12px;
            }

            QPushButton:checked {
                background-color: #3E4048;
            }
        """)

        # тень
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

    def _init_animation(self):
        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._base_pos = None

    def enterEvent(self, event):
        if self._base_pos is None:
            self._base_pos = self.pos()

        self._anim.stop()
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(self._base_pos + QPoint(0, -2))
        self._anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._base_pos is None:
            return

        self._anim.stop()
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(self._base_pos)
        self._anim.start()

        super().leaveEvent(event)