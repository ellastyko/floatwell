from PyQt5.QtCore import QObject, pyqtSignal

class UIController(QObject):
    mode = pyqtSignal(str)

class AppLogDispatcher(QObject):
    log_message = pyqtSignal(str, str)
    clear_logs  = pyqtSignal()

# Глобальный синглтон
ui          = UIController()
applog      = AppLogDispatcher()
