from qt.style import StyleManager
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize, Qt
from qt.tools import colorize_icon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

class PushButton(QPushButton):
    def __init__(self, text = None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.__init_ui()

    def __init_ui(self):
        self.setStyleSheet(StyleManager.get_style("QPushButton"))

class NavButton(QPushButton):
    def __init__(self, icon_path, tooltip=None):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        if tooltip:
            self.setToolTip(tooltip)
        
        # --- Icons ---
        icon = QIcon()
        icon.addPixmap(colorize_icon(icon_path, "#8a8a8a"), QIcon.Normal)
        icon.addPixmap(colorize_icon(icon_path, "#ffffff"), QIcon.Active)

        self.setIcon(icon)
        self.setIconSize(QSize(30, 30))

        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(50, 50)
        self.setObjectName("NavButton")
        self.setAttribute(Qt.WA_StyledBackground, True) 

        self.setStyleSheet("""
            #NavButton {
                border: 2px solid transparent;
            }
            #NavButton:checked {
                border-left: 2px solid white;
            }
        """)
    
class SidebarButton(QPushButton):
    def __init__(self, icon_path: str, tooltip=None):
        super().__init__()
# colors: dict,
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)

        icon = QIcon()
        icon.addPixmap(colorize_icon(icon_path, "#8a8a8a"), QIcon.Normal)
        icon.addPixmap(colorize_icon(icon_path, "#ffffff"), QIcon.Active)
        self.setIcon(icon)
        self.setIconSize(QSize(30, 30))

        if tooltip:
            self.setToolTip(tooltip)

        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(44, 44)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._update_style()

    def _update_style(self):
        self.setObjectName("SidebarButton")
        self.setStyleSheet("""
            #SidebarButton {
                background-color: #2F3136;
                color: #f8faff;
                border: none;
                border-radius: 22px;
                font-weight: 600;
                text-align: center;
            }
            #SidebarButton:hover {
                background-color: #3E4048;
            }
            #SidebarButton:pressed {
                background-color: #57585f;
            }
        """)
