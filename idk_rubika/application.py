import asyncio
import logging
import json
from typing import List

from .bot import RubikaBot
from .context import CallbackContext
from .handlers import Handler
from .models import Update
from .storage import OffsetStore


class Application(RubikaBot):

    def __init__(self, token: str,timeout: int = 30, base_url: str = "https://botapi.rubika.ir/v3/"):
        super().__init__(token, timeout, base_url)
        self.token = token
        self.base_url = base_url
        self.handlers: List[Handler] = []
        self._offset_id = ""
        self._running = False
        self.bot_info = self.get_me()
        self.bot_username: str = self.bot_info.username or "unknown_bot"
        self.offset_store = OffsetStore()
        self._offset_id: str = self.offset_store.load(self.bot_username)
        self.message_database.create_table(
            "message",
            {
                "id": "TEXT",
                "chat_id": "TEXT", 
                "data": "TEXT"
            }
        )

        logging.info(
            "Loaded offset for @%s: %s", self.bot_username, self._offset_id or "(empty)"
        )


    def do_for_messages_database(self,update: Update):

        if update.new_message:
            message = update.new_message
        elif update.updated_message:
            message = update.updated_message
        else:
            if update.removed_message_id:
                self.message_database.remove(
                    "message",{"id": update.removed_message_id,"chat_id":update.chat_id}
                )
                return
            return
        
        self.message_database.set("message",{
            'id': message.message_id,
            'chat_id': update.chat_id,
            'data': json.dumps(message.data, ensure_ascii=False)
        })
        
    

    def _save_offset(self):
        """offset فعلی رو روی دیسک ذخیره می‌کنه."""
        if self._offset_id:
            self.offset_store.save(self.bot_username, self._offset_id)
    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    async def _process_update(self, update: Update):
        context = CallbackContext(self, update)
        for handler in self.handlers:
            if handler.check(update):
                try:
                    await handler.callback(update, context)
                except Exception as error:
                    logging.error("Error in handler: %s", error, exc_info=True)

    async def _drain_pending_updates(self, max_rounds: int = 20):
        """Discard old pending updates and keep the latest server offset."""
        logging.info("Draining pending updates...")
        probe_offset = self._offset_id  # از offset ذخیره‌شده شروع کن
        last_offset = self._offset_id

        for _ in range(max_rounds):
            try:
                updates, next_offset = await self.get_updates(
                    offset_id=probe_offset, limit=100
                )

                if not updates:
                    logging.info("No more pending updates. Drain complete.")
                    self._offset_id = next_offset or last_offset
                    self._save_offset()
                    return

                if not next_offset:
                    logging.warning(
                        "Drain stopped because the response did not contain next_offset_id."
                    )
                    self._offset_id = last_offset
                    self._save_offset()
                    return

                last_offset = next_offset
                probe_offset = next_offset
                self._offset_id = next_offset
                self._save_offset()
                logging.info(
                    "Drained %s pending updates, offset=%s", len(updates), last_offset
                )

            except Exception as error:
                logging.error("Error during drain: %s", error, exc_info=True)
                self._offset_id = last_offset
                self._save_offset()
                return

        logging.warning(
            "Drain reached max rounds; there might still be pending updates."
        )
        self._offset_id = last_offset
        self._save_offset()

    def run_polling(self, poll_interval: float = 1.0, drop_pending: bool = True):
        asyncio.run(self._run_polling(poll_interval, drop_pending))

    async def _run_polling(self, poll_interval: float = 1.0, drop_pending: bool = True):
        if poll_interval < 0:
            raise ValueError("poll_interval cannot be negative")

        if drop_pending:
            await self._drain_pending_updates()

        self._running = True
        logging.info(
            "Bot @%s started polling from offset=%s",
            self.bot_username,
            self._offset_id or "(empty)",
        )

        while self._running:
            try:
                updates, next_offset = await self.get_updates(
                    offset_id=self._offset_id, limit=100
                )

                for update in updates:
                    await self._process_update(update)
                    self.do_for_messages_database(update)

                if next_offset:
                    self._offset_id = next_offset
                    self._save_offset()

                await asyncio.sleep(poll_interval)

            except Exception as error:
                logging.error("Polling error: %s", error, exc_info=True)
                await asyncio.sleep(5)

        def stop(self):
            self._running = False

    def stop(self):
        self._running = False
