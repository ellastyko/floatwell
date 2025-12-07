from PyQt5.QtCore import QObject, pyqtSignal
import time
from parsers.listings import Listings, Analyzer
import json 

def load_config():
    """Загружаем интересующие паттерны (int_value) из файла"""
    with open(ANALYZER_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

EXTERIORS = [
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
]

ANALYZER_CONFIG_FILE = "./assets/analizer_config.json"

class ParserWorker(QObject):
    data_parsed = pyqtSignal(list)   # сигнал при обновлении данных
    finished    = pyqtSignal()       # если нужно корректно завершить поток

    def __init__(self):
        super().__init__()
        self._running = True

        self.config = load_config()

        self.listings = Listings()
        self.analyzer = Analyzer(self.config)

    def stop(self):
        self._running = False

    def run(self):
        """Основной цикл парсинга"""
        while self._running:
            self.parse_listings()

    def parse_listings(self):
        while True:
            for item_group_name in self.config.keys():
                for exterior in EXTERIORS:
                    hash_name = f"{item_group_name} ({exterior})"

                    data = self.listings.get(hash_name)

                    if data:
                        data_to_display = [] 

                        for item in data:
                            pattern_rank = self.analyzer.is_rare_pattern(item_group_name, item['pattern'])
                            rare_float = self.analyzer.is_rare_float(item_group_name, exterior, item['float'])

                            if pattern_rank and item['price']:
                                # item['is_highlighted'] = False

                                if pattern_rank and item['price']:
                                    item['pattern'] = f"{ item['pattern']} ({pattern_rank})"

                                converted_price = int(item['price']) / 100 * 41
                                item['price'] = f"{converted_price:.2f} UAH"

                                data_to_display.append(item)

                        self.data_parsed.emit(data_to_display)
                    
                    time.sleep(1)
                    
            time.sleep(120)