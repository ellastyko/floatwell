import asyncio
import threading
import queue
from dataclasses import dataclass
from typing import Iterable, Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError


@dataclass
class BotEvent:
    level: str  # info | warn | error | progress
    text: str
    meta: Optional[Dict[str, Any]] = None


class TelegramBotService:
    def __init__(
        self,
        token: str,
        whitelist_chat_ids: Iterable[int],
        flush_interval: float = 0.3,
    ):
        """
        :param token: Telegram bot token
        :param whitelist_chat_ids: chat_id list allowed to receive messages
        :param flush_interval: seconds between queue flushes
        """
        self.bot = Bot(token=token)
        self.whitelist = set(whitelist_chat_ids)
        self.flush_interval = flush_interval

        self._queue: queue.Queue[BotEvent] = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ---------------- Public API (safe from PyQt thread) ----------------

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def notify(self, text: str, level: str = "info", meta: dict | None = None):
        """Main entry point from PyQt code"""
        print('notification')
        self._queue.put(BotEvent(level=level, text=text, meta=meta))

    def info(self, text: str):
        self.notify(text, "info")

    def warn(self, text: str):
        self.notify(text, "warn")

    def error(self, text: str, meta: dict | None = None):
        self.notify(text, "error", meta)

    def progress(self, text: str, percent: int | None = None):
        if percent is not None:
            text = f"{text} ({percent}%)"
        self.notify(text, "progress")

    # ---------------- Internal ----------------

    def _worker(self):
        """
        Runs in a separate thread.
        Owns its own asyncio event loop.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._loop.create_task(self._dispatcher())
        self._loop.run_forever()

    async def _dispatcher(self):
        """
        Async task that pulls events from the queue
        and sends them to Telegram.
        """
        while self._running:
            try:
                event = self._queue.get(timeout=self.flush_interval)
            except queue.Empty:
                await asyncio.sleep(0)
                continue

            message = self._format(event)

            for chat_id in self.whitelist:
                try:
                    res = await self.bot.send_message(
                        chat_id=chat_id,
                        text=message
                    )
                    print(res)

                except TelegramError:
                    # Telegram may be unavailable — ignore by design
                    pass

    @staticmethod
    def _format(event: BotEvent) -> str:
        icon = {
            "info": "ℹ️",
            "warn": "⚠️",
            "error": "❌",
            "progress": "⏳",
        }.get(event.level, "ℹ️")

        msg = f"{icon} {event.text}"
        if event.meta:
            for k, v in event.meta.items():
                msg += f"\n• {k}: {v}"
        return msg

from core.settings import settings_manager

bot = TelegramBotService(token=settings_manager.get('telegram.BOT_TOKEN'))