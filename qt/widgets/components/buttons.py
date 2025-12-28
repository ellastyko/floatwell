from qt.style import StyleManager
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize, Qt

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
        self.setObjectName("NavButton")
        self.setAttribute(Qt.WA_StyledBackground, True) 

        self.setStyleSheet("""
            #NavButton {
                background-color: #2F3136;
                border: none;
                border-radius: 12px;
            }

            #NavButton:checked {
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

class SidebarButton(QPushButton):
    def __init__(self, icon=None, tooltip=None, label=None):
        super().__init__()
        self.icon = icon
        self.label = label
        self.expanded = True  # состояние сайдбара

        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)

        if self.icon:
            self.setIcon(self.icon)
            self.setIconSize(QSize(24, 24))
        if tooltip:
            self.setToolTip(tooltip)

        self._init_ui()
        self._init_animation()

    def _init_ui(self):
        self.setFixedSize(44, 44)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._update_style()

        # тень
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self.shadow)

    def _init_animation(self):
        self._anim = QPropertyAnimation(self, b"minimumWidth")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_expanded(self, expanded: bool):
        """Меняем состояние кнопки: expanded/collapsed"""
        self.expanded = expanded
        self._animate_width()

    def _animate_width(self):
        start_width = self.width()
        end_width = 160 if self.expanded else 44
        self._anim.stop()
        self._anim.setStartValue(start_width)
        self._anim.setEndValue(end_width)
        self._anim.start()

        # текст только в expanded
        self.setText(self.label if self.expanded else "")

        # тень для компактного вида
        self.setGraphicsEffect(self.shadow if self.expanded else None)

    def _update_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #2F3136;
                color: #f8faff;
                border: none;
                border-radius: 22px;
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3E4048;
            }
            QPushButton:pressed {
                background-color: #57585f;
            }
        """)

    # Можно добавить небольшой подъем при hover, как в NavButton
    # def enterEvent(self, event):
    #     self.move(self.x(), self.y() - 2)
    #     super().enterEvent(event)

    # def leaveEvent(self, event):
    #     self.move(self.x(), self.y() + 2)
    #     super().leaveEvent(event)