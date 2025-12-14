import random, threading
from datetime import datetime, UTC, timedelta
from utils.logs import log
from configurator import config
from utils.helpers import load_json_resource

class ProxyContext:
    def __init__(self, proxy, sem, last_used):
        self.proxy = proxy
        self._sem = sem
        self._last_used = last_used
        self._started_at = datetime.now(UTC)

    def __enter__(self):
        return self.proxy

    def __exit__(self, exc_type, exc_val, exc_tb):
        prx = f"{self.proxy['ip']}:{self.proxy['port']}"

        finished_at = datetime.now(UTC)
        duration_ms = int((finished_at - self._started_at).total_seconds() * 1000)

        # 🔹 обновляем last_used
        self._last_used[prx] = finished_at

        # 🔹 лог
        log(
            f"🧷 Proxy {prx} released | "
            f"duration={duration_ms}ms | "
            f"time={finished_at.strftime('%H:%M:%S')}"
        )

        self._sem.release()


class ProxyService:
    def __init__(self, max_concurrent_per_proxy=1, cooldown_seconds=12):
        self.max_concurrent_per_proxy = max_concurrent_per_proxy
        self.cooldown_seconds = cooldown_seconds

        self._semaphores = {}
        self._last_used = {}
        self._lock = threading.Lock()

        self.proxies = load_json_resource(config['resources']['proxies'])

    def acquire(self) -> ProxyContext | None:
        with self._lock:
            proxies = self.proxies[:]
            random.shuffle(proxies)

            for proxy in proxies:
                prx = f"{proxy['ip']}:{proxy['port']}"
                now = datetime.now(UTC)

                if prx not in self._semaphores:
                    self._semaphores[prx] = threading.Semaphore(self.max_concurrent_per_proxy)

                if prx not in self._last_used:
                    self._last_used[prx] = now - timedelta(seconds=self.cooldown_seconds + 1)

                if (now - self._last_used[prx]).total_seconds() < self.cooldown_seconds:
                    continue

                sem = self._semaphores[prx]
                if not sem.acquire(blocking=False):
                    continue

                return ProxyContext(proxy, sem, self._last_used)

            return None

proxy_service = ProxyService()