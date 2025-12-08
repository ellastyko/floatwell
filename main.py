import sys
from PyQt5.QtWidgets import QApplication
from qt.window import MainWindow
from PyQt5 import QtGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("./assets/images/logo.jpg"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
