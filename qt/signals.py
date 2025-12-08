from PyQt5.QtCore import QObject, pyqtSignal

class UIController(QObject):
    mode = pyqtSignal(str)

class EventDispatcher(QObject):
    # Location preview
    title_changed = pyqtSignal(str)
    image_changed = pyqtSignal(str)

    # Settings
    map_changed       = pyqtSignal(str)
    model_changed     = pyqtSignal(str)
    dataset_type      = pyqtSignal(str)
    show_connections  = pyqtSignal(bool)

    connections_status = pyqtSignal(str)

class AppLogSignals(QObject):
    log_message = pyqtSignal(str, str)
    clear_logs  = pyqtSignal()

# Глобальный синглтон
ui          = UIController()
applog      = AppLogSignals()
dispatcher  = EventDispatcher()
