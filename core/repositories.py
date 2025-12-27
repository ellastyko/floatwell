from qt.signals import table_dispatcher
from qt.notifier import short_notify
from core.source.manager import source_manager

class ListingsRepository:
    def __init__(self):
        self.listings = {}  # key = listing_id, value = item_data
        self.source_globals = source_manager.get_globals()

    def add(self, listings: list):
        filtered_listings = self._filter_new(listings)

        if len(filtered_listings) < 1:
            return
        
        # Prepare data for preview in table
        rows = self._prepare_for_preview(filtered_listings)
        table_dispatcher.items_table.emit(rows)

        short_notify(f"{filtered_listings[0]['name']}", f"Listings added ({len(rows)})")

    # 
    # Filter old listings
    # 
    def _filter_new(self, listings: list):
        new_listings = []
        for listing in listings:
            listing_id = listing["listing_id"]
            if listing_id in self.listings:
                self.listings[listing_id].update(listing)
            else:
                self.listings[listing_id] = listing
                new_listings.append(listing)  # новые элементы
        return new_listings  # возвращаем только новые, чтобы уведомить пользователя
    
    # 
    # Prepare data for preview in table
    # 
    def _prepare_for_preview(self, listings):
        rows = []
        for listing in listings:
            csymbol    = listing['currency']['symbol']
            price_diff = f"{listing['pricediff'] * 100:.1f}"

            if listing.get('has_rare_pattern'):
                pattern_col = f"{listing['pattern']} ({listing['patterninfo']['rank']})"
            else:
                pattern_col = listing['pattern']

            rows.append({
                'name':             listing['hash_name'],
                'image':            listing['image'],
                'listing_id':       listing['listing_id'],
                'assets':           listing['assets'],
                'float':            listing['float'],
                'pattern':          pattern_col,
                'converted_price':  f"{listing['converted_min_price']}{csymbol} -> {listing['converted_price']}{csymbol} ({price_diff}%)",
                'inspect_link':     listing['inspect_link'],
                'buy_url':          listing['buy_url'],
                'sync_at':          listing['sync_at'],
            })

        return rows
    

class ProxyRepository:
    def __init__(self):
        # key = ip:port
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

        rows = self._prepare_for_preview(new_proxies)
        table_dispatcher.proxies_table_insert.emit(rows)

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

        rows = self._prepare_for_preview(updated)
        table_dispatcher.proxies_table_update.emit(rows)

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
            table_dispatcher.proxies_table_insert.emit(
                self._prepare_for_preview(new_items)
            )

        if updated_items:
            table_dispatcher.proxies_table_update.emit(
                self._prepare_for_preview(updated_items)
            )

    # ---------------- Helpers ---------------- #

    def _prepare_for_preview(self, proxies: list[dict]) -> list[dict]:
        rows = []
        for proxy in proxies:
            rows.append({
                'ip': proxy['ip'],
                'port': proxy['port'],
                'country_code': proxy.get('country_code'),
                'username': proxy.get('username'),
                'password': proxy.get('password'),
                'total_requests': proxy.get('total_requests'),
                'success_rate': proxy.get('success_rate'),
                'last_used_at': proxy.get('last_used_at'),
            })
        return rows

    @staticmethod
    def _key(proxy: dict) -> str:
        return f"{proxy['ip']}:{proxy['port']}"

proxy_repository = ProxyRepository()