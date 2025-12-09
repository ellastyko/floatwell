import asyncio, random
from datetime import datetime, UTC, timedelta
from typing import Optional, List
from utils.logs import log
from utils.helpers import load_json_resource

class ProxyService:
    """
    Сервис управления прокси для асинхронных запросов.
    Основная цель:
    - обеспечить безопасное использование прокси
    - учитывать cooldown
    - лимитировать количество одновременных запросов через один прокси
    - логировать использование прокси в ProxyRequest
    """

    def __init__(self, max_concurrent_per_proxy: int = 1, cooldown_seconds: int = 12, retry_delay: int = 5):
        self.max_concurrent_per_proxy = max_concurrent_per_proxy
        self.cooldown_seconds = cooldown_seconds
        self.retry_delay = retry_delay

        self._semaphores: dict[int, asyncio.Semaphore] = {}   # proxy_id -> semaphore
        self._last_used: dict[int, datetime] = {}             # proxy_id -> last used
        self._lock = asyncio.Lock()                           # защита от гонок при выдаче прокси

    async def _load_active_proxies(self):
        """Загружаем все активные прокси из БД"""
        self.proxies = load_json_resource(self.PROXIES)

    async def wrap(self, task_fn, *args, **kwargs):
        """
        Оборачивает задачу в цикл получения прокси.
        task_fn — async-функция, которая принимает proxy как первый аргумент.
        """
        while True:
            proxy_ctx = await self.get_proxy()
            if proxy_ctx is None:
                log("⚠ Нет доступных прокси, ждем...")
                await asyncio.sleep(self.retry_delay)
                continue

            async with proxy_ctx as proxy:
                return await task_fn(proxy, *args, **kwargs)

    async def get_proxy(self):
        """
        Получить готовый к использованию прокси.
        Берем первый доступный прокси с учетом семафора и cooldown.
        """
        async with self._lock:
            proxies = await self._load_active_proxies()

            random.shuffle(proxies)

            # logger.info('ITERATION')
            for proxy in proxies:
                now = datetime.now(UTC)
                prx = f"{proxy['ip']}:{proxy['port']}"

                # Инициализация семафора и времени последнего использования
                if prx not in self._semaphores:
                    self._semaphores[prx] = asyncio.Semaphore(self.max_concurrent_per_proxy)

                if prx not in self._last_used:
                    self._last_used[prx] = now - timedelta(seconds=self.cooldown_seconds + 1)

                time_since_last_use = (now - self._last_used[prx]).total_seconds()
                sem = self._semaphores[prx]

                # logger.info(f'PROXY CHECK {proxy.ip} --- last request was {time_since_last_use:.3f}s ago --- Is locked - {sem.locked()}')

                # Проверяем cooldown
                if time_since_last_use < self.cooldown_seconds:
                    continue

                # Проверяем семафор
                if sem.locked():
                    continue

                # Захватываем слот
                await sem.acquire()

                # Оборачиваем прокси в объект с контекстным менеджером для автоматического релиза
                class ProxyContext:
                    def __init__(self, proxy, sem, last_used_dict):
                        self.proxy = proxy
                        self._sem = sem
                        self._last_used_dict = last_used_dict

                    async def __aenter__(self):
                        return self.proxy

                    async def __aexit__(self, exc_type, exc_val, exc_tb):
                        prx = f"{proxy['ip']}:{proxy['port']}"
                        # Обновляем last_used и освобождаем семафор
                        self._last_used_dict[prx] = datetime.now(UTC)
                        self._sem.release()

                return ProxyContext(proxy, sem, self._last_used)

            log("❌ Нет свободных прокси")
            return None

    async def release_proxy(self, proxy, success: bool = True, endpoint: str = None, response_time_ms: int = None, error_message: str = None):
        """
        Освобождение прокси после использования и логирование ProxyRequest
        """
        prx = f"{proxy['ip']}:{proxy['port']}"

        async with self._lock:
            if prx in self._semaphores:
                self._semaphores[prx].release()
                log(f"🔸 Прокси {prx} освобождён")

# Singleton для всего приложения
proxy_service = ProxyService(max_concurrent_per_proxy=1, cooldown_seconds=13)
