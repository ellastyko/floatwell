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

from dataclasses import dataclass

@dataclass(frozen=True)
class SidebarButtonTheme:
    bg_normal: str = "#2F3136"
    bg_hover: str = "#3E4048"
    bg_active: str = "#57585f"

    icon_normal: str = "#8a8a8a"
    icon_active: str = "#ffffff"

    button_size: tuple = (44, 44)
    icon_size: tuple = (30, 30)

class SidebarButton(QPushButton):
    def __init__(
        self,
        icon_path: str,
        tooltip: str | None = None,
        checked=False,
        theme: SidebarButtonTheme = SidebarButtonTheme()
    ):
        super().__init__()

        self.theme = theme
        self.icon_path = icon_path

        self.setCursor(Qt.PointingHandCursor)
        
        self.setCheckable(True)
        self.setChecked(checked)

        self._init_icon()
        self._init_ui()

        if tooltip:
            self.setToolTip(tooltip)
    
    def _init_icon(self):
        self._icon_normal = QIcon(colorize_icon(self.icon_path, self.theme.icon_normal))
        self._icon_active = QIcon(colorize_icon(self.icon_path, self.theme.icon_active))

        self._update_icon()

        w, h = self.theme.icon_size
        self.setIconSize(QSize(w, h))
    
    def _update_icon(self):
        self.setIcon(
            self._icon_active if self.isChecked() else self._icon_normal
        )

    def _init_ui(self):
        w, h = self.theme.button_size
        self.setFixedSize(w, h)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.toggled.connect(self._update_icon)

        self.setObjectName("SidebarButton")
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QPushButton#SidebarButton {{
                background-color: {self.theme.bg_normal};
                border: none;
                text-align: center;
                border-radius: 22px;
            }}
            QPushButton#SidebarButton:hover {{
                background-color: {self.theme.bg_hover};
            }}
            QPushButton#SidebarButton:checked {{
                background-color: {self.theme.bg_active};
            }}
        """)

