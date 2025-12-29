from PyQt5.QtCore import QObject, pyqtSignal

class Repository(QObject):
    added   = pyqtSignal(list)     # новые листинги (raw)
    updated = pyqtSignal(list)

class ListingsRepository(Repository):
    def __init__(self):
        super().__init__()
        self.listings = {}  # key = listing_id, value = item_data

    def upsert(self, listings: list):
        new_items = []
        updated_items = []

        for listing in listings:
            lid = listing["listing_id"]

            if lid in self.listings:
                self.listings[lid].update(listing)
                updated_items.append(self.listings[lid])
            else:
                self.listings[lid] = listing
                new_items.append(listing)

        if new_items:
            self.added.emit(new_items)

        if updated_items:
            self.updated.emit(updated_items)

class ProxyRepository(Repository):
    def __init__(self):
        # key = ip:port
        super().__init__()
        self.proxies: dict[str, dict] = {}

    # ---------------- Public API ---------------- #

    def insert(self, proxies: list[dict]):
        """
        Обрабатывает только НОВЫЕ прокси
        """
        new_proxies = []

        for proxy in proxies:
            key = self._key(proxy)
            if key in self.proxies:
                continue

            self.proxies[key] = proxy
            new_proxies.append(proxy)

        if not new_proxies:
            return

        self.added.emit(new_proxies)

    def update(self, proxies: list[dict]):
        """
        Обновляет ТОЛЬКО существующие прокси
        """
        updated = []

        for proxy in proxies:
            key = self._key(proxy)
            stored = self.proxies.get(key)

            if not stored:
                continue

            stored.update(proxy)
            updated.append(stored)

        if not updated:
            return

        self.updated.emit(updated)

    def upsert(self, proxies: list[dict]):
        """
        Удобный метод, если прилетает всё сразу
        """
        new_items = []
        updated_items = []

        for proxy in proxies:
            key = self._key(proxy)

            if key in self.proxies:
                self.proxies[key].update(proxy)
                updated_items.append(self.proxies[key])
            else:
                self.proxies[key] = proxy
                new_items.append(proxy)

        if new_items:
            self.added.emit(new_items)

        if updated_items:
            self.updated.emit(updated_items)

    # ---------------- Helpers ---------------- #

    @staticmethod
    def _key(proxy: dict) -> str:
        return f"{proxy['ip']}:{proxy['port']}"

proxy_repository    = ProxyRepository()
listings_repository = ListingsRepository()