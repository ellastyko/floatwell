import sys, os
from PyQt5.QtWidgets import QApplication
from qt.window import MainWindow
from PyQt5 import QtGui
from utils.helpers import resource_path
from configurator import config

# # -------------------------------
# # Создаём папку для логов
# logs_path = os.path.join(os.path.abspath("."), "storage", "logs")
# os.makedirs(logs_path, exist_ok=True)
# # -------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path(config['main']['icon'])))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
