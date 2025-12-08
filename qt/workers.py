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
    ANALYZER_CONFIG_FILE = "./assets/configs/analizer.json"
    PROXIES              = "./assets/proxies.json"

    finished    = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = False
        self.config  = load_json_resource(self.ANALYZER_CONFIG_FILE)
        self.proxies = load_json_resource(self.PROXIES)

        self.listings = Listings()
        self.analyzer = Analyzer(self.config)

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
        for item_group_name in self.config.keys():
            for exterior in EXTERIORS:
                hash_name, data = f"{item_group_name} ({exterior})", None

                while data is None:
                    data = self.listings.get(hash_name, 'UAH', random.choice(self.proxies))
                    time.sleep(1)

                data_to_display = [] 

                min_price = min(item['converted_price'] for item in data if item.get('converted_price'))

                for item in data:
                    # Извлекаем основную информацию
                    pattern_info = self.analyzer.get_pattern_info(item_group_name, item['pattern'])
                    float_info   = self.analyzer.get_float_info(item_group_name, exterior, item['float'])
                    # Добавить инфу о брелках и тд

                    if pattern_info['is_rear'] or float_info['is_rear']:
                        diff = price_difference(item['converted_price'], min_price)

                        # Если цена не соответствует ожиданиям скипаем
                        if pattern_info['price_tolerance'] < diff:
                            continue

                        data_to_display.append({
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

                listing_repository.add_items.emit(data_to_display)
                
                time.sleep(12)
