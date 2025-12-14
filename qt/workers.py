from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import random
from datetime import datetime

from core.listings import ListingsParser, ListingAnalyzer
from utils.helpers import load_json_resource
from utils.market import price_difference
from configurator import config
from qt.repositories import ListingsRepository
from core.source import source_manager
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
    finished = pyqtSignal()

    REQUEST_DELAY_MS = 3000
    RETRY_DELAY_MS   = 1000
    ITERATION_DELAY  = 60_000

    def __init__(self):
        super().__init__()
        self._running = False
        self._tasks   = []
        self._timer   = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._process_next_task)

        self.proxies = load_json_resource(config['resources']['proxies'])

    # -------------------- public API --------------------

    def run(self):
        try:
            self._running = True
            self._setup()
            self._build_tasks()
            self._process_next_task()
        except Exception as e:
            log(e)
            self.stop()

    def stop(self):
        self._running = False
        self._tasks.clear()
        self._timer.stop()
        self.finished.emit()

    # -------------------- setup --------------------

    def _setup(self):
        print('_setup')

        self.currency   = settings_manager.get('currency')
        self.repository = ListingsRepository()
        self.listings   = ListingsParser()
        self.analyzer   = ListingAnalyzer()

        if not source_manager.is_source_valid():
            raise Exception("Invalid source")

        self.source_filters        = source_manager.get_filters()
        self.source_configurations = source_manager.get_configurations()

    # -------------------- task queue --------------------

    def _build_tasks(self):
        print('_build_tasks')

        self._tasks.clear()

        for cname, config in self.source_configurations.items():
            if not config.get('is_active', True):
                continue

            if config.get('has_exteriors'):
                for exterior in EXTERIORS:
                    self._tasks.append((cname, config, exterior))
            else:
                self._tasks.append((cname, config, None))

    def _process_next_task(self):
        print('_process_next_task')

        if not self._running:
            return self.finished.emit()

        if not self._tasks:
            # новая итерация через минуту
            QTimer.singleShot(self.ITERATION_DELAY, self._restart_iteration)
            return

        cname, configuration, exterior = self._tasks.pop(0)
        self.analyzer.set_configuration(configuration)

        self._parse_single(cname, exterior)

    def _restart_iteration(self):
        if not self._running:
            return self.finished.emit()

        self._build_tasks()
        self._process_next_task()

    # -------------------- parsing --------------------

    def _parse_single(self, item_name, exterior):
        print('_parse_single')
        if not self._running:
            return

        hash_name = f"{item_name} ({exterior})" if exterior else item_name
        proxy     = random.choice(self.proxies)

        data = self.listings.get(hash_name, self.currency, proxy)
        print(data)

        if data is None:
            # retry без блокировки
            self._timer.start(self.RETRY_DELAY_MS)
            return

        result = self._analyze_items(data, exterior)
        self.repository.add_items.emit(result)

        # задержка перед следующей задачей
        self._timer.start(self.REQUEST_DELAY_MS)

    # -------------------- analysis --------------------

    def _analyze_items(self, data, exterior):
        result = []

        min_price = min(i.get('converted_price', float('inf')) for i in data)
        min_float = min(i.get('float', float('inf')) for i in data)

        for item in data:
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
                "name": item['name'],
                "listing_id": item['listing_id'],
                "assets": item['assets'],
                "buy_url": item['buy_url'],
                "inspect_link": item['inspect_link'],
                "pattern": pattern_info,
                "float": float_info,
                "currency": self.currency,
                "diff": diff,
                "converted_min_price": min_price,
                "converted_price": item['converted_price'],
                "sync_at": datetime.now().strftime("%H:%M:%S"),
            })

        applog.log_message.emit(
            f"{data[0]['name']}; Parsed {len(data)} items, {len(result)} featured | Lowest float: {min_float}",
            "info"
        )

        return result
