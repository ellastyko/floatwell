from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from io import BytesIO
from core.image import image_loader

class AssetsCellWidget(QWidget):
    ICON_SIZE = 28

    def __init__(self, assets: list):
        super().__init__()

        self.labels = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignLeft)
        # self.setFixedHeight(36)

        for asset in assets:
            label = QLabel()
            label.setFixedSize(self.ICON_SIZE, self.ICON_SIZE)
            label.setToolTip(asset["name"])
            label.setAlignment(Qt.AlignCenter)

            # placeholder
            label.setStyleSheet("background:#2b2b2b; border-radius:4px;")

            self.labels[asset["image"]] = label
            layout.addWidget(label)

            image_loader.load(asset["image"])

        layout.addStretch()

        image_loader.image_loaded.connect(self._on_image_loaded)

    def _on_image_loaded(self, url, pixmap):
        if url not in self.labels:
            return

        self.labels[url].setPixmap(
            pixmap.scaled(
                self.ICON_SIZE,
                self.ICON_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

class ItemCellWidget(QWidget):
    IMAGE_HEIGHT = 28

    def __init__(self, image_url: str, name: str):
        super().__init__()

        self.image_url = image_url
        self.name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft)

        # --- Картинка ---
        self.image_label = QLabel()
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.image_label.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_label.setFixedWidth(self.IMAGE_HEIGHT)
        layout.addWidget(self.image_label)

        # --- Название ---
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.name_label.setStyleSheet("color: #EEE; background: transparent;")
        layout.addWidget(self.name_label)

        layout.addStretch()

        # --- Подписка на сигнал перед загрузкой ---
        image_loader.image_loaded.connect(self._on_image_loaded)
        image_loader.load(self.image_url)

        # --- Если уже в кэше, сразу ставим ---
        if self.image_url in image_loader.cache:
            self._set_pixmap(image_loader.cache[self.image_url])

    def _on_image_loaded(self, url, pixmap):
        if url != self.image_url:
            return
        self._set_pixmap(pixmap)
        image_loader.image_loaded.disconnect(self._on_image_loaded)  # больше не слушаем

    def _set_pixmap(self, pixmap):
        self.image_label.setPixmap(
            pixmap.scaled(
                self.IMAGE_HEIGHT,
                self.IMAGE_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
