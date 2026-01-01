from PyQt5.QtCore import QObject
from core.repositories import listings_repository
from core.notifications.notifier import notification_queue
from core.settings import settings_manager
from core.telegram.bot import bot

class ListingsNotificationSubscriber(QObject):
    def __init__(self):
        super().__init__()

        listings_repository.added.connect(self.on_added)

    def on_added(self, items: list):
        if settings_manager.get('notifications.windows', True):
            count = len(items)
            first = items[0]['hash_name']

            notification_queue.push(
                title=first,
                message=f"Listings added ({count})",
            )

        if settings_manager.get('notifications.telegram', False):
            count = len(items)
            first = items[0]['hash_name']

            bot.notify(f"Listings added ({count})")