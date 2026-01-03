import asyncio
import threading
import queue
from dataclasses import dataclass
from typing import Iterable, Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from jinja2 import Environment, FileSystemLoader, select_autoescape
from utils.logs import log

@dataclass
class BotEvent:
    level: str
    template: str
    context: Dict[str, Any]


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
        self.flush_interval = flush_interval
        self.init_bot(token)
        self.set_whitelist(whitelist_chat_ids)

        self.jinja = Environment(
            loader=FileSystemLoader("resources/templates/telegram"),
            autoescape=select_autoescape(enabled_extensions=("html",))
        )

        self._queue: queue.Queue[BotEvent] = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def init_bot(self, token: str):
        self.bot = Bot(token=token)
    
    def set_whitelist(self, whitelist_chat_ids: Iterable[int]):
        self.whitelist = set(whitelist_chat_ids)

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

    def notify(
        self,
        template: str,
        level: str = "info",
        context: Dict[str, Any] | None = None
    ):
        self._queue.put(
            BotEvent(
                level=level,
                template=template,
                context=context or {}
            )
        )

    def info(self, template: str, **context):
        self.notify(template, "info", context)

    def error(self, template: str, **context):
        self.notify(template, "error", context)

    def progress(self, template: str, **context):
        self.notify(template, "progress", context)

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
            
            message = self._render(event)

            for chat_id in self.whitelist:
                try:
                    res = await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                except TelegramError as e:
                    log(e)
                    # Telegram may be unavailable — ignore by design
                    pass

    def _render(self, event: BotEvent) -> str:
        tpl = self.jinja.get_template(f"{event.template}.html")
        return tpl.render(**event.context)

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

bot = TelegramBotService(token=settings_manager.get('telegram.BOT_TOKEN'), whitelist_chat_ids=settings_manager.get('telegram.CHAT_IDS'))