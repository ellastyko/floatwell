import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QFrame, QHBoxLayout
)
from utils.market import format_price
from PyQt5.QtCore import Qt, QPoint, QEvent, QRect, QUrl
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from qt.widgets.components.buttons import PushButton
from core.image import image_loader
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation

class FloatingPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        QApplication.instance().installEventFilter(self)

        self._setup_effects()

    def _setup_effects(self):
        # Тень для современного вида
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self.setObjectName("FloatingPreview")
        self.setStyleSheet("""
            #FloatingPreview {
                background: transparent;
                border: none;
            }
        """)

        # Начальная прозрачность 0 (невидима)

        self.anim_geometry = QPropertyAnimation(self, b"geometry")
        self.anim_geometry.setDuration(200)
        self.anim_geometry.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_show_group = QParallelAnimationGroup(self)
        self.anim_show_group.addAnimation(self.anim_geometry)

        self.anim_hide_group = QParallelAnimationGroup(self)
        self.anim_hide_group.finished.connect(super().hide)

        self._target_geometry = QRect()
    
    def _load_image(self, url: str | None):
        self.image.clear()

        if not url:
            self._set_placeholder()
            return

        self._current_image_url = url
        self.image.setText("Loading…")

        image_loader.load(url)
    
    def _set_placeholder(self):
        self.image.setText("NO IMAGE")
    
    def _on_image_loaded(self, url: str, pixmap: QPixmap):
        if url != self._current_image_url:
            return  # ответ не для текущего превью

        if pixmap.isNull():
            self._set_placeholder()
            return

        pixmap = pixmap.scaled(
            self.image.width(),
            self.image.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image.setPixmap(pixmap)
        self._fade_in_image()
    
    def _fade_in_image(self):
        effect = QGraphicsOpacityEffect(self.image)
        self.image.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self.image)
        anim.setDuration(140)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def open_link(self, url: str | None):
        if not url:
            return
        QDesktopServices.openUrl(QUrl(url))

    def smart_move(self, anchor: QPoint, offset_x=12, offset_y=0):
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        bounds = screen.availableGeometry()
        x = anchor.x() + offset_x
        y = anchor.y() + offset_y
        if x + self.width() > bounds.right():
            x = anchor.x() - self.width() - offset_x
        if y + self.height() > bounds.bottom():
            y = anchor.y() - self.height() - offset_y
        x = max(bounds.left() + 8, min(x, bounds.right() - self.width() - 8))
        y = max(bounds.top() + 8, min(y, bounds.bottom() - self.height() - 8))
        self._target_geometry = QRect(x, y, self.width(), self.height())

    def animated_show(self):
        self.anim_hide_group.stop()
        self.anim_show_group.stop()

        start_rect = self._scaled_geometry(0.92)
        self.setGeometry(start_rect)
        self.show()
        self.raise_()

        self.anim_geometry.setStartValue(start_rect)
        self.anim_geometry.setEndValue(self._target_geometry)
        self.anim_show_group.start()

    def animated_hide(self):
        if self.isVisible():
            self.anim_show_group.stop()
            self.anim_hide_group.start()

    def _scaled_geometry(self, scale):
        g = self._target_geometry
        w, h = int(g.width()*scale), int(g.height()*scale)
        x = g.center().x() - w//2
        y = g.center().y() - h//2
        return QRect(x, y, w, h)

    def eventFilter(self, obj, event):
        if self.isVisible():
            if event.type() == QEvent.MouseButtonPress:
                if not self.geometry().contains(event.globalPos()):
                    self.animated_hide()
            if event.type() in (QEvent.ApplicationDeactivate, QEvent.WindowDeactivate):
                self.animated_hide()
        return super().eventFilter(obj, event)


class ItemFloatingPreview(FloatingPreview):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(260, 340)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # ===== CARD CONTAINER =====
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            #card {
                background-color: #181818;
                border-radius: 12px;
            }
        """)
        root.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # ===== ITEM NAME =====
        self.name = QLabel()
        self.name.setWordWrap(True)
        self.name.setMaximumHeight(36)
        self.name.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.name)

        # ===== IMAGE =====
        self._current_image_url = None
        image_loader.image_loaded.connect(self._on_image_loaded)

        self.image = QLabel()
        self.image.setFixedHeight(120)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setStyleSheet("""
            QLabel {
                background-color: #101010;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.image)

        # ===== INFO BLOCK =====
        info = QVBoxLayout()
        info.setSpacing(2)

        self.price = QLabel()
        self.price.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #7ddc8c;
            }
        """)

        self.pattern = QLabel()
        self.float_lbl = QLabel()

        for lbl in (self.pattern, self.float_lbl):
            lbl.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #9a9a9a;
                }
            """)

        info.addWidget(self.price)
        info.addWidget(self.pattern)
        info.addWidget(self.float_lbl)

        layout.addLayout(info)
        layout.addStretch(1)

        # ===== ACTION BUTTONS =====
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(6)

        self.inspect_btn = PushButton("Inspect")
        self.remove_btn = PushButton("Remove")

        buttons_row.addWidget(self.inspect_btn)
        buttons_row.addWidget(self.remove_btn)

        layout.addLayout(buttons_row)

        # ===== BUY BUTTON =====
        self.buy_btn = PushButton("On Steam")

        layout.addWidget(self.buy_btn)

        # ===== LINKS =====
        self._inspect_url = None
        self._buy_url = None
        self.buy_btn.clicked.connect(lambda: self.open_link(self._buy_url))
        self.inspect_btn.clicked.connect(lambda: self.open_link(self._inspect_url))

    def show_data(self, data: dict, pos: QPoint):
        self.set_data(data)
        self.smart_move(pos)
        self.animated_show()

    def set_data(self, data: dict):
        self.name.setText(data.get('short_hash_name', '—'))

        self.price.setText(f"Price: {format_price(data.get('converted_price', 0), data.get('currency', {}).get('code'), 'uk_UA')}")
        self.pattern.setText(f"Pattern: {data.get('pattern', '—')}")

        float_val = data.get('float')
        self.float_lbl.setText(
            f"Float: {float_val:.4f}" if isinstance(float_val, (int, float)) else "Float: —"
        )

        self._buy_url = data.get('buy_url')
        self._inspect_url = data.get('inspect_link')

        self._load_image(data.get('image'))
