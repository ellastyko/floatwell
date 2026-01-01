from core.notifications.subscribers import ListingsNotificationSubscriber

# Global register
class AppServiceProvider:
    def __init__(self):
        self.subscribers = [
            ListingsNotificationSubscriber(),
        ]
