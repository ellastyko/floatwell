from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime

from core.listings import ListingsParser, ListingAnalyzer
from utils.helpers import load_json_resource
from utils.market import price_difference
from configurator import config
from core.repositories import ListingsRepository
from core.repositories import proxy_repository
from core.proxy import proxy_service
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

    REQUEST_DELAY_MS = 500
    RETRY_DELAY_MS   = 500
    ITERATION_DELAY  = 10_000

    def __init__(self):
        super().__init__()
        self._running = False
        self._tasks   = []

    # -------------------- public API --------------------

    def run(self):
        try:
            self._running = True

            self._timer = QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._process_next_task)

            self._setup()
            self._build_tasks()
            self._process_next_task()
        except Exception as e:
            log(e)
            self.stop()

    def stop(self):
        self._running = False
        self._tasks.clear()
        self.finished.emit()

    # -------------------- setup --------------------

    def _setup(self):
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
        if not self._running:
            return

        hash_name = f"{item_name} ({exterior})" if exterior else item_name

        proxy_ctx = proxy_service.acquire()
        if proxy_ctx is None:
            applog.log_message.emit('❌ Нет свободных прокси', 'warning')
            self._timer.start(self.RETRY_DELAY_MS)
            return

        with proxy_ctx as proxy:
            data = self.listings.get(hash_name, self.currency, proxy)

            proxy_ctx.report(False) if data is None else proxy_ctx.report(True)
        
        # Update proxy stats
        stats = proxy_service.get_stats(proxy)

        proxy_repository.update([{
            **proxy,
            'success_rate': stats.success_rate,
            'last_used_at': stats.last_used_at,
        }])

        if data is None:
            # retry без блокировки
            self._timer.start(self.RETRY_DELAY_MS)
            return

        result = self._analyze_items(data, exterior)

        # Add items to repository
        self.repository.add(result)

        # задержка перед следующей задачей
        self._timer.start(self.REQUEST_DELAY_MS)

    # -------------------- analysis --------------------

    def _analyze_items(self, data, exterior):
        result = []

        min_price = min(i.get('converted_price', float('inf')) for i in data)

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
            f"{data[0]['name']}; Parsed {len(data)} items, {len(result)} featured",
            "info"
        )

        return result
