from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time, random
from core.listings import ListingsParser, ListingAnalyzer
from utils.helpers import load_json_resource
from utils.market import price_difference
from datetime import datetime
from qt.repositories import listing_repository
from configurator import config
from core.source import source_manager
from PyQt5.QtWidgets import QApplication
from core.settings import settings_manager

EXTERIORS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

class ListingWorker(QObject):
    finished     = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = False
        self.proxies  = load_json_resource(config['resources']['proxies'])

    def stop(self):
        self._running = False
    
    def run(self):
        self._running = True
        self._setup()
        self._run_iteration()
    
    def _setup(self):
        self.currency = settings_manager.get('currency')
        self.listings = ListingsParser()
        self.analyzer = ListingAnalyzer()
        
        # Создаем флаг ожидания
        self.source_loaded = False
        
        def on_source_loaded(success, filename):
            self.source_loaded = True
            if not success:
                print(f"Ошибка загрузки {filename}")
        
        # Временно подключаемся к сигналу
        source_manager.source_loaded.connect(on_source_loaded)
        source_manager.source_changed.emit('rare.json')
        
        # Ждем завершения (осторожно: может зависнуть!)
        while not self.source_loaded:
            QApplication.processEvents()  # Обрабатываем события Qt
        
        source_manager.source_loaded.disconnect(on_source_loaded)
        
        # Теперь данные точно загружены
        self.source_filters = source_manager.get_filters()
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
                    listing_repository.add_items.emit(self.parse_single(cname, exterior))
                    time.sleep(3)
            else:
                listing_repository.add_items.emit(self.parse_single(cname))
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
                'currency_code':       item['currency']['code'],
                'diff':                diff,
                'converted_min_price': min_price, 
                'converted_price':     item['converted_price'], 
                'sync_at':             datetime.now().strftime("%H:%M:%S")
            })

        return result
