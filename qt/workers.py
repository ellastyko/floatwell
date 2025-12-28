from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime

from core.listings import ListingsParser
from core.filters import ListingAnalyzer
from utils.market import price_difference
from configurator import config
from core.repositories import ListingsRepository
from core.repositories import proxy_repository
from core.proxy import proxy_service
from core.source.manager import source_manager
from core.settings import settings_manager
from utils.logs import log
from utils.market import match_rule
from qt.signals import applog
from core.strategies import STRATEGY_REGISTRY, StrategyContext

class ListingWorker(QObject):
    finished = pyqtSignal()

    REQUEST_DELAY_MS = 50
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
        self.parser     = ListingsParser()

        if not source_manager.is_source_valid():
            raise Exception("Invalid source")

        self.source_globals    = source_manager.get_globals()
        self.source_strategies = source_manager.get_active_strategies()
        self.source_assets     = source_manager.get_assets()
        # Aliases is FN, exteriors is Factory New
        self.exterior_aliases  = source_manager.get_exterior_aliases()
        self.exteriors         = source_manager.get_exteriors()

        self.analyzer = ListingAnalyzer(self.source_globals, self.source_assets)


    # -------------------- task queue --------------------

    def _build_tasks(self):
        self._tasks.clear()

        for cname, config in self.source_assets.items():
            if not config.get('enabled', True):
                continue

            has_exteriors = config.get('has_exteriors', True)

            if has_exteriors:
                exterior_aliases = config.get('exteriors', self.exterior_aliases)
                
                for ext in exterior_aliases:
                    self._tasks.append((cname, ext, 0, config.get('multipage', False))) 
            else:
                self._tasks.append((cname, None, 0, config.get('multipage', False)))

    def _process_next_task(self):
        if not self._running:
            return self.finished.emit()

        if not self._tasks:
            # новая итерация через минуту
            QTimer.singleShot(self.ITERATION_DELAY, self._restart_iteration)
            return

        cname, exterior_alias, start, multipage = self._tasks.pop(0)

        self._parse_single(cname, exterior_alias, start, multipage)

    def _restart_iteration(self):
        if not self._running:
            return self.finished.emit()

        self._build_tasks()
        self._process_next_task()

    # -------------------- parsing --------------------


    def _parse_single(self, item_name, exterior_alias: str|None, start: int, multipage: bool):
        if not self._running:
            return

        # Преобразовываем exterior из FN в Factory New
        suffix = self.exteriors[exterior_alias] if exterior_alias else None

        hash_name = f"{item_name} {suffix}" if suffix else item_name

        proxy_ctx = proxy_service.acquire()
        if proxy_ctx is None:
            applog.log_message.emit('❌ Нет свободных прокси', 'warning')
            self._timer.start(self.RETRY_DELAY_MS)
            return

        with proxy_ctx as proxy:
            data, meta = self.parser.get(hash_name, self.currency, proxy, start)

            proxy_ctx.report(False) if data is None else proxy_ctx.report(True)
        
        # Update proxy stats
        stats = proxy_service.get_stats(proxy)

        proxy_repository.update([{
            **proxy,
            'success_rate': stats.success_rate,
            'total_requests': stats.total,
            'last_used_at': stats.last_used_at,
        }])

        # Обработка запроса вызвавшего исключение
        if data is None:
            self._tasks.insert(0, (item_name, exterior_alias, start, multipage))
            self._timer.start(self.RETRY_DELAY_MS)
            return
        
        # Обработка запроса не вернувшего никаких предметов
        if not data:
            self._timer.start(self.RETRY_DELAY_MS)
            return

        # Data processing
        result = self._process_data(item_name, exterior_alias, data, meta)
        # Add items to repository
        self.repository.add(result)

        if multipage and meta['has_more']:
            self._tasks.append((item_name, exterior_alias, start + meta['per_page'], multipage))

        # задержка перед следующей задачей
        self._timer.start(self.REQUEST_DELAY_MS)

    # -------------------- analysis --------------------

    def _process_data(self, item_name, exterior, data, meta):
        # Data analysis
        analized = self.analyzer.apply(item_name, exterior, data)

        result = []

        strategies = [
            STRATEGY_REGISTRY[name]()
            for name in self.source_strategies
            if name in STRATEGY_REGISTRY
        ]

        for item in analized['items']:
            ctx = StrategyContext(item)

            if not all(strategy.applies(ctx) for strategy in strategies):
                continue

            cycle_data = {"currency": self.currency, "sync_at": datetime.now().strftime("%H:%M:%S"), 'converted_min_price': analized['converted_min_price']}

            result.append({**item, **cycle_data})
        
        applog.log_message.emit(
            f"{analized['hash_name']}; Parsed {len(analized['items'])} items, {len(result)} featured (page {int(meta['page'])})",
            "info"
        )

        return result
