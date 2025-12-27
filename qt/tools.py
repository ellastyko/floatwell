from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

def colorize_icon(icon_path, color, size=40):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    icon = QIcon(icon_path)
    icon.paint(painter, 0, 0, size, size)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)