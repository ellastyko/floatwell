from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer

class SessionTime(QLabel):
    def __init__(self):
        super().__init__()
        self.seconds = 0
        self.__init_ui()
        self.__init_timer()

    def __init_ui(self):
        self.setAlignment(Qt.AlignVCenter)
        self.setStyleSheet("""
            padding: 0 8px;               
            color: #8E9297;
            background: transparent;
            border: none;
        """)
        self.setText("Session: 00:00:00")

    def __init_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # обновлять каждую секунду

    def update_time(self):
        self.seconds += 1
        self.setText(f"Session: {self.format_time(self.seconds)}")

    @staticmethod
    def format_time(total):
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class AppVersionLabel(QLabel):
    def __init__(self, version: str):
        super().__init__(f"Float Flower v{version}")
        self.setStyleSheet("""
            QLabel {
                padding: 0 8px;  
                color: #8E9297;      /* приглушённый discord-style */
                padding-right: 6px;
                background: transparent;
            }
        """)