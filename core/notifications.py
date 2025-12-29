from PyQt5.QtCore import QObject
from windows_toasts import ToastDuration
from core.repositories import listings_repository
from core.notifier import notifier

class NotificationSubscribtionService:
    def __init__(self):
        self.subscribers = [
            ListingsNotificationSubscriber(),
            # другие подписчики
        ]

class ListingsNotificationSubscriber(QObject):
    def __init__(self):
        super().__init__()

        listings_repository.added.connect(self.on_added)

    def on_added(self, items: list):
        count = len(items)
        first = items[0]['hash_name']

        notifier.notify(
            title=first,
            message=f"Listings added ({count})",
            duration=ToastDuration.Short
        )
