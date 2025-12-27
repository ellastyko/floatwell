from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap

class ImageLoader(QObject):
    image_loaded = pyqtSignal(str, QPixmap)

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.cache = {}

    def load(self, url: str):
        if url in self.cache:
            self.image_loaded.emit(url, self.cache[url])
            return

        request = QNetworkRequest(QUrl(url))
        reply = self.manager.get(request)
        reply.finished.connect(lambda: self._on_finished(reply, url))

    def _on_finished(self, reply, url):
        if reply.error():
            reply.deleteLater()
            return

        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        self.cache[url] = pixmap
        self.image_loaded.emit(url, pixmap)
        reply.deleteLater()

image_loader = ImageLoader()