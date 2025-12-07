from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class Connections(QLabel):
    def __init__(self):
        super().__init__()
        self.__init_ui()
        self.setText(f"Agents connected: 0")

    def __init_ui(self):
        self.setAlignment(Qt.AlignVCenter)
        self.setStyleSheet("""
            padding: 0 8px;
        """)

    def change_status(self, count):
        # Change status label
        return self.setText(f"Agents connected: {count}")

