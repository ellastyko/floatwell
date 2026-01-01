from collections import deque
from PyQt5.QtCore import QObject, QTimer
from windows_toasts import (
    Toast,
    WindowsToaster,
    ToastDisplayImage,
    ToastDuration,
)

from configurator import config
from utils.helpers import resource_path
from utils.window import focus


class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.enabled = True
        self.toaster = WindowsToaster(config['main']['appname'])

    def notify(self, title: str, message: str, duration=ToastDuration.Short):
        if not self.enabled:
            print("[NOTIFIER] disabled, skip")
            return

        print(f"[NOTIFIER] SHOW -> '{title}' | '{message}'")

        toast = Toast()
        toast.AddImage(
            ToastDisplayImage.fromPath(
                resource_path(config['main']['icon'])
            )
        )
        toast.text_fields = [title, message]
        toast.duration = duration
        toast.on_activated = lambda args: focus()

        self.toaster.show_toast(toast)


class NotificationQueue(QObject):
    """
    - Показывает одиночные уведомления при малом потоке
    - Агрегирует, если сообщений много за короткое время
    """

    AGGREGATION_THRESHOLD = 4
    AGGREGATION_WINDOW_MS = 5000
    DISPATCH_INTERVAL_MS = 2500

    def __init__(self):
        super().__init__()

        self._queue = deque()
        self._notifier = Notifier()

        self._generation = 0
        self._aggregate_first_title = None

        self._dispatch_timer = QTimer()
        self._dispatch_timer.setInterval(self.DISPATCH_INTERVAL_MS)
        self._dispatch_timer.timeout.connect(self._dispatch_next)

        self._aggregate_timer = QTimer()
        self._aggregate_timer.setSingleShot(True)
        self._aggregate_timer.setInterval(self.AGGREGATION_WINDOW_MS)
        self._aggregate_timer.timeout.connect(self._flush_aggregate)

    # ===== PUBLIC API =====

    def push(self, title: str, message: str):
        gen = self._generation
        self._queue.append((gen, title, message))

        print(f"[QUEUE] push gen={gen} size={len(self._queue)} title='{title}'")

        if self._aggregate_first_title is None:
            self._aggregate_first_title = title

        if not self._aggregate_timer.isActive():
            self._aggregate_timer.start()

        if not self._dispatch_timer.isActive():
            self._dispatch_timer.start()
        
    
    def clear(self):
        print(
            f"[QUEUE] CLEAR gen {self._generation} -> {self._generation + 1} "
            f"(drop {len(self._queue)})"
        )

        self._generation += 1
        self._queue.clear()
        self._aggregate_first_title = None

        self._dispatch_timer.stop()
        self._aggregate_timer.stop()

    # ===== INTERNAL =====

    def _dispatch_next(self):
        if not self._queue:
            self._dispatch_timer.stop()
            return

        gen, title, message = self._queue.popleft()

        if gen != self._generation:
            print(f"[DISPATCH] DROP phantom gen={gen}")
            return

        print(f"[DISPATCH] SEND '{title}'")

        self._notifier.notify(
            title=title,
            message=message,
            duration=ToastDuration.Short
        )

    def _flush_aggregate(self):
        count = len(self._queue)

        if count < self.AGGREGATION_THRESHOLD:
            return

        print(f"[AGGREGATE] SEND aggregated count={count}")

        self._queue.clear()
        self._aggregate_first_title = None

        self._notifier.notify(
            title="Notifications",
            message=f"+{count} messages",
            duration=ToastDuration.Short
        )




# ===== ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР =====

notification_queue = NotificationQueue()
