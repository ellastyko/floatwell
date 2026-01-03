from PyQt5.QtCore import QObject
from core.repositories import listings_repository
from core.notifications.notifier import notification_queue
from core.settings import settings_manager
from core.telegram.bot import bot

class ListingsNotificationSubscriber(QObject):
    def __init__(self):
        super().__init__()

        listings_repository.added.connect(self.on_added)

    def on_added(self, listings: list):
        if settings_manager.get('notifications.desktop', False):
            count = len(listings)
            first = listings[0]['hash_name']

            notification_queue.push(
                title=first,
                message=f"Listings added ({count})",
            )

        if settings_manager.get('notifications.telegram', False):
            bot.start()

            for listing in listings:
                bot.info(
                    "listing",
                    short_hash_name=listing["short_hash_name"],
                    pattern=listing["pattern"],
                    float=listing["float"],
                    has_rare_pattern=listing["has_rare_pattern"],
                    patterninfo=listing.get("patterninfo"),
                    buy_url=listing["buy_url"],
                    converted_price=listing["converted_price"],
                    pricediff=listing["pricediff"],
                    currency=listing["currency"],
                )
        else:
            bot.stop()