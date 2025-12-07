import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from win10toast import ToastNotifier

class NotificationDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Notifications Demo")
        self.setGeometry(300, 300, 300, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button = QPushButton("Show Notification")
        self.button.clicked.connect(self.show_notification)
        self.layout.addWidget(self.button)

        self.notifier = ToastNotifier()

    def show_notification(self):
        self.notifier.show_toast(
            "PyQt5 Notification",
            "Hello! This is a Windows toast notification.",
            duration=5,      # секунд отображения
            threaded=True    # чтобы не блокировать GUI
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotificationDemo()
    window.show()
    sys.exit(app.exec_())
