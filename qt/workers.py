from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time, random
from parsers.listings import Listings, Analyzer
from utils.helpers import load_json_resource
from utils.market import price_difference
import humanize
from datetime import datetime, timedelta
from qt.repositories import listing_repository

EXTERIORS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

class ListingWorker(QObject):
    ITEMS_SOURCE = "./assets/configs/rare.json"
    PROXIES      = "./assets/proxies.json"

    finished    = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = False
        self.source  = load_json_resource(self.ITEMS_SOURCE)
        self.proxies = load_json_resource(self.PROXIES)

        self.listings = Listings()
        self.analyzer = Analyzer(self.source['data'])

    def stop(self):
        self._running = False
    
    def run(self):
        self._running = True
        self._run_iteration()

    def _run_iteration(self):
        if not self._running:
            self.finished.emit()
            return
        
        self.parse_listings()  
        # через 600 секунд запустить следующую итерацию
        QTimer.singleShot(600_000, self._run_iteration)

    def parse_listings(self):
        self.source_filters = self.source['filters']

        # loader.set_max(len(self.source['data']) * len(EXTERIORS))
        # loader.set_value_signal(0)

        for item_name, item_config in self.source['data'].items():
            result = []

            if item_config['has_exteriors']:
                for exterior in EXTERIORS:
                    result.extend(self.parse_single(item_name, exterior))
            else:
                result.extend(self.parse_single(item_name))

            listing_repository.add_items.emit(result)
            
            time.sleep(12)

    def parse_single(self, item_name, exterior = None):
        hash_name, data = f"{item_name} ({exterior})" if exterior else item_name, None

        while data is None:
            data = self.listings.get(hash_name, 'UAH', random.choice(self.proxies))
            
            if data is None:
                time.sleep(1) 
            else:
                break 
        
        # loader.set_value_signal(loader.get_value() + 1)

        result = [] 

        min_price = min(item.get('converted_price', float('inf')) for item in data)

        for item in data:
            # Извлекаем основную информацию
            pattern_info = self.analyzer.get_pattern_info(item_name, item['pattern'], exterior)
            float_info   = self.analyzer.get_float_info(item_name, item['float'], exterior)
            # Добавить инфу о брелках и тд

            diff = price_difference(item['converted_price'], min_price)

            if 'pattern' in self.source_filters and (pattern_info['is_rear'] is False or pattern_info['price_tolerance'] < diff):
                continue
            # if 'float' in self.source_filters and not float_info['is_rear']:
            #     continue
            if 'keychains' in self.source_filters and not item['has_keychain']:
                continue
            if 'stickers' in self.source_filters and not item['has_sticker']:
                continue
            
            result.append({
                "name":         item['name'],
                "listing_id":   item['listing_id'],
                'assets':       item['assets'],
                'buy_url':      item['buy_url'],
                'inspect_link': item['inspect_link'],
                'pattern':      pattern_info,
                'float':        float_info,
                'currency_code':       item['currency']['code'],
                'diff':                diff,
                'converted_min_price': min_price, 
                'converted_price':     item['converted_price'], 
                'sync_at':             datetime.now().strftime("%H:%M:%S")
            })

        return result
