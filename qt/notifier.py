from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QTimer
from win10toast_persist import ToastNotifier
import threading

class NotificationSignals(QObject):
    notify = pyqtSignal(str, str, int)

class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.signals = NotificationSignals()
        self.toast = ToastNotifier()
        self.signals.notify.connect(self._show_notification, Qt.QueuedConnection)

    @pyqtSlot(str, str, int)
    def _show_notification(self, title, message, duration=5):
        # запускаем в отдельном потоке, чтобы не блокировать PyQt
        threading.Thread(target=self._notify, args=(title, message, duration), daemon=True).start()

    def _notify(self, title, message, duration):
        self.toast.show_toast(title, message, duration=duration, threaded=True)

    def send(self, title, message, duration=5):
        self.signals.notify.emit(title, message, duration)

notifier = Notifier()

def safe_notify(title, message, timeout=5):
    QTimer.singleShot(0, lambda: notifier.send(title, message, timeout))
