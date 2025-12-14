from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time, random
from core.listings import ListingsParser, ListingAnalyzer
from utils.helpers import load_json_resource
from utils.market import price_difference
from datetime import datetime
from configurator import config
from qt.repositories import ListingsRepository
from core.source import source_manager
from PyQt5.QtWidgets import QApplication
from core.settings import settings_manager
from utils.logs import log
from qt.signals import applog

EXTERIORS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

class ListingWorker(QObject):
    finished = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = False
        self.proxies  = load_json_resource(config['resources']['proxies'])

    def stop(self):
        self._running = False
        self.finished.emit()
    
    def run(self):
        try:
            self._running = True
            self._setup()
            self._run_iteration()
        except Exception as e:
            log(e)
            self.stop()
    
    def _setup(self):
        self.currency   = settings_manager.get('currency')
        self.repository = ListingsRepository()
        self.listings   = ListingsParser()
        self.analyzer   = ListingAnalyzer()
        
        if not source_manager.is_source_valid():
            raise Exception('Invalid source')
        
        # Теперь данные точно загружены
        self.source_filters        = source_manager.get_filters()
        self.source_configurations = source_manager.get_configurations()

    def _run_iteration(self):
        if not self._running:
            self.finished.emit()
            return

        self.parse_listings()  
        # через 600 секунд запустить следующую итерацию
        QTimer.singleShot(60_000, self._run_iteration)

    def parse_listings(self):
        for cname, configuration in self.source_configurations.items():
            if configuration.get('is_active') is False:
                continue
            
            self.analyzer.set_configuration(configuration)

            if configuration['has_exteriors']:
                for exterior in EXTERIORS:
                    self.repository.add_items.emit(self.parse_single(cname, exterior))
                    time.sleep(3)
            else:
                self.repository.add_items.emit(self.parse_single(cname))
                time.sleep(3)
            
    def parse_single(self, item_name, exterior = None):
        hash_name, data = f"{item_name} ({exterior})" if exterior else item_name, None

        while data is None:
            data = self.listings.get(hash_name, self.currency, random.choice(self.proxies))
            
            if data is None:
                time.sleep(1) 
            else:
                break 
        
        result = [] 

        min_price = min(item.get('converted_price', float('inf')) for item in data)
        min_float = min(item.get('float', float('inf')) for item in data)

        for item in data:
            # Извлекаем основную информацию
            pattern_info = self.analyzer.get_pattern_info(item['pattern'], exterior)
            float_info   = self.analyzer.get_float_info(item['float'], exterior)
            diff         = price_difference(item['converted_price'], min_price)

            score = 0

            if 'pattern' in self.source_filters and pattern_info['is_rear'] and pattern_info['price_tolerance'] > diff:
                score += 1
            if 'float' in self.source_filters and float_info['is_rear']:
                score += 1
            if 'keychains' in self.source_filters and item['has_keychain']:
                score += 1
            if 'stickers' in self.source_filters and item['has_sticker']:
                score += 1
            
            if score < 1:
                continue
            
            result.append({
                "name":         item['name'],
                "listing_id":   item['listing_id'],
                'assets':       item['assets'],
                'buy_url':      item['buy_url'],
                'inspect_link': item['inspect_link'],
                'pattern':      pattern_info,
                'float':        float_info,
                'currency':     self.currency,
                'diff':                diff,
                'converted_min_price': min_price, 
                'converted_price':     item['converted_price'], 
                'sync_at':             datetime.now().strftime("%H:%M:%S")
            })

        log_message = f"{item['name']}; Parsed {len(data)} items, {len(result)} are featured | Lowest float: {min_float}"
        applog.log_message.emit(log_message, 'info')

        return result
