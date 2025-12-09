from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QTimer
import threading
from windows_toasts import Toast, WindowsToaster
from configurator import config
from utils.helpers import resource_path

class NotificationSignals(QObject):
    notify = pyqtSignal(str, str, int)

class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.signals = NotificationSignals()
        # WindowsToaster принимает идентификатор приложения
        self.toaster = WindowsToaster(config['main']['appname'])
        self.signals.notify.connect(self._show_notification, Qt.QueuedConnection)

    @pyqtSlot(str, str, int)
    def _show_notification(self, title, message, duration=5):
        # запускаем в отдельном потоке, чтобы не блокировать PyQt
        threading.Thread(target=self._notify, args=(title, message, duration), daemon=True).start()

    def _notify(self, title, message, duration):
        toast = Toast()
        toast.image_path  = resource_path(config['main']['icon'])
        toast.text_fields = [title, message]
        # duration в windows-toasts не задаётся напрямую, но можно эмулировать
        # через QTimer или просто показывать toast (он сам исчезает)
        self.toaster.show_toast(toast)

    def send(self, title, message, duration=5):
        self.signals.notify.emit(title, message, duration)

# глобальный экземпляр
notifier = Notifier()

def safe_notify(title, message, timeout=5):
    QTimer.singleShot(0, lambda: notifier.send(title, message, timeout))
