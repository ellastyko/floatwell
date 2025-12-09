from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar

class LoadingBar(QWidget):
    # Сигналы для внешнего управления
    set_max_signal = pyqtSignal(int)
    set_value_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading Bar")
        self.setGeometry(200, 200, 100, 150)

        layout = QVBoxLayout(self)

        self.progress = QProgressBar(self)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Подключаем сигналы к слотам
        self.set_max_signal.connect(self.progress.setMaximum)
        self.set_value_signal.connect(self.progress.setValue)
    
    def get_value(self):
        return self.progress.value()

    def set_max(self, value: int):
        """Задать максимальную шкалу"""
        self.set_max_signal.emit(value)

    def update_progress(self, value: int):
        """Обновить прогресс"""
        self.set_value_signal.emit(value)
