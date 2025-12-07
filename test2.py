import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton
from PyQt5.QtCore import QBasicTimer

class LoadingBarDemo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Loading Bar")
        self.setGeometry(200, 200, 400, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setMaximum(100)
        self.layout.addWidget(self.progress)

        # Start Button
        self.button = QPushButton("Start Loading", self)
        self.button.clicked.connect(self.start_loading)
        self.layout.addWidget(self.button)

        # Timer
        self.timer = QBasicTimer()
        self.step = 0

    def start_loading(self):
        if not self.timer.isActive():
            self.step = 0
            self.progress.setValue(0)
            self.timer.start(100, self)  # timeout every 100ms

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
        else:
            self.step += 1
            self.progress.setValue(self.step)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadingBarDemo()
    window.show()
    sys.exit(app.exec_())
