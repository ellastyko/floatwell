from PyQt5.QtCore import QObject, pyqtSignal

class UIController(QObject):
    mode = pyqtSignal(str)

class AppLogDispatcher(QObject):
    log_message = pyqtSignal(str, str)
    clear_logs  = pyqtSignal()

class ItemsTableDispatcher(QObject):
    items_table   = pyqtSignal(list)
    proxies_table = pyqtSignal(list)

table_dispatcher = ItemsTableDispatcher()

# Глобальный синглтон
ui          = UIController()
applog      = AppLogDispatcher()
