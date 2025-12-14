from PyQt5.QtCore import QObject, pyqtSignal
from qt.signals import table_dispatcher
from qt.notifier import short_notify

class ListingsRepository(QObject):
    add_items = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.items = {}  # key = listing_id, value = item_data

        self.add_items.connect(self.on_items_added)

    def on_items_added(self, items: list):
        items = self.filter_new(items)

        if len(items) < 1:
            return

        rows = []
        for item in items:
            csymbol = item['currency']['symbol']
            price_diff = f"{item['diff'] * 100:.1f}"

            if item['pattern']['is_rear']:
                pattern_col = f"{ item['pattern']['value']} ({item['pattern']['rank']})"
            else:
                pattern_col = item['pattern']['value']

            rows.append({
                'name_col': item['name'],
                'listing_id_col': item['listing_id'],
                'assets_col': ", ".join(item["name"] for item in item['assets']),
                'float_col': item['float']['value'],
                'pattern_col': pattern_col,
                'converted_price_col': f"{item['converted_min_price']}{csymbol} -> {item['converted_price']}{csymbol} ({price_diff}%)",
                'inspect_link_col': item['inspect_link'],
                'buy_url_col': item['buy_url'],
                'sync_at_col': item['sync_at'],
            })
        
        table_dispatcher.items_table.emit(rows)

        short_notify(f"{item['name']}", f"Listings added ({len(rows)})")

    def filter_new(self, items: list):
        new_items = []
        for item in items:
            listing_id = item["listing_id"]
            if listing_id in self.items:
                self.items[listing_id].update(item)
            else:
                self.items[listing_id] = item
                new_items.append(item)  # новые элементы
        return new_items  # возвращаем только новые, чтобы уведомить пользователя
