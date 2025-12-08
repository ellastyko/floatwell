from PyQt5.QtCore import QObject, pyqtSignal
import time
from parsers.listings import Listings, Analyzer
from utils import load_config, price_difference, convert_price
import random

EXTERIORS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

class ParserWorker(QObject):
    ANALYZER_CONFIG_FILE = "./assets/configs/analizer.json"
    PROXIES              = "./assets/proxies.json"

    data_parsed = pyqtSignal(list)   # сигнал при обновлении данных
    finished    = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = True

        self.config  = load_config(self.ANALYZER_CONFIG_FILE)
        self.proxies = load_config(self.PROXIES)

        self.listings = Listings()
        self.analyzer = Analyzer(self.config)

    def stop(self):
        self._running = False

    def run(self):
        """Основной цикл парсинга"""
        while self._running:
            self.parse_listings()

            time.sleep(120)

    def parse_listings(self):
        for item_group_name in self.config.keys():
            for exterior in EXTERIORS:
                hash_name, data = f"{item_group_name} ({exterior})", None

                while data is None:
                    data = self.listings.get(hash_name, random.choice(self.proxies))
                    time.sleep(6)

                data_to_display = [] 

                min_price = min(item['price'] for item in data if item.get('price'))

                for item in data:
                    # Извлекаем основную информацию
                    pattern_info = self.analyzer.get_pattern_info(item_group_name, item['pattern'])
                    float_info   = self.analyzer.get_float_info(item_group_name, exterior, item['float'])
                    # Добавить инфу о брелках и тд

                    if pattern_info['is_rear'] or float_info['is_rear']:
                        diff = price_difference(item['price'], min_price)

                        # Если цена не соответствует ожиданиям скипаем
                        if pattern_info['price_tolerance'] < diff:
                            continue

                        if pattern_info['is_rear']:
                            item['pattern'] = f"{ item['pattern']} ({pattern_info['rank']})"

                        item['converted_min_price'] = f"{convert_price(min_price, 41)} UAH"
                        item['converted_price'] = f"{item['converted_min_price']} -> {convert_price(item['price'], 41)} UAH ({diff * 100:.1f}%)"

                        data_to_display.append(item)

                self.data_parsed.emit(data_to_display)
                
                time.sleep(12)
