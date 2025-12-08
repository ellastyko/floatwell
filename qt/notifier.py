# notifier.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from win10toast import ToastNotifier


class NotificationSignals(QObject):
    """Сигналы для межпоточных уведомлений."""
    notify = pyqtSignal(str, str, int)   # title, message, duration


class Notifier(QObject):
    """Изолированный модуль Windows-уведомлений."""
    def __init__(self):
        super().__init__()
        self.signals = NotificationSignals()
        self.toast = ToastNotifier()

        # подключаем сигнал к слоту
        self.signals.notify.connect(self._show_notification, type=self.signals.notify.QueuedConnection)

    @pyqtSlot(str, str, int)
    def _show_notification(self, title, message, duration=5):
        """Потокобезопасный показ уведомлений."""
        try:
            self.toast.show_toast(
                title,
                message,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            print(f"Notification error: {e}")

    def send(self, title: str, message: str, duration: int = 5):
        """Вызов уведомления из любого места/потока."""
        self.signals.notify.emit(title, message, duration)


# Глобальный экземпляр, чтобы можно было импортировать напрямую
notifier = Notifier()
