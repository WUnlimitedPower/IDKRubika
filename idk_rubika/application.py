import asyncio
import logging
from typing import List

from .bot import RubikaBot
from .context import CallbackContext
from .handlers import Handler
from .models import Update


class Application:
    def __init__(self, token: str, base_url: str = "https://botapi.rubika.ir/v3/"):
        self.token = token
        self.base_url = base_url
        self.handlers: List[Handler] = []
        self._offset_id = ""
        self._running = False
        self.bot = RubikaBot(token, base_url)

    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    async def _process_update(self, update: Update):
        context = CallbackContext(self.bot, update)
        for handler in self.handlers:
            if handler.check(update):
                try:
                    await handler.callback(update, context)
                except Exception as error:
                    logging.error("Error in handler: %s", error, exc_info=True)

    async def _drain_pending_updates(self, max_rounds: int = 20):
        """Discard old pending updates and keep the latest server offset."""
        logging.info("Draining pending updates...")
        probe_offset = ""
        last_offset = ""

        for _ in range(max_rounds):
            try:
                response = await asyncio.to_thread(
                    self.bot.get_updates, offset_id=probe_offset, limit=100
                )
                if response.get("status") == "INVALID_INPUT":
                    logging.warning("Drain skipped: INVALID_INPUT from server.")
                    self._offset_id = last_offset
                    return

                data = response.get("data", {})
                updates = data.get("updates", [])
                next_offset = data.get("next_offset_id")

                if not updates:
                    logging.info("No more pending updates. Drain complete.")
                    self._offset_id = next_offset or last_offset
                    return

                if not next_offset:
                    logging.warning(
                        "Drain stopped because the response did not contain next_offset_id."
                    )
                    self._offset_id = last_offset
                    return

                last_offset = next_offset
                probe_offset = next_offset
                logging.info(
                    "Drained %s pending updates, offset=%s", len(updates), last_offset
                )

            except Exception as error:
                logging.error("Error during drain: %s", error, exc_info=True)
                self._offset_id = last_offset
                return

        logging.warning(
            "Drain reached max rounds; there might still be pending updates."
        )
        self._offset_id = last_offset

    async def run_polling(self, poll_interval: float = 1.0, drop_pending: bool = True):
        if poll_interval < 0:
            raise ValueError("poll_interval cannot be negative")

        if drop_pending:
            await self._drain_pending_updates()

        self._running = True
        logging.info("Bot started polling...")

        while self._running:
            try:
                response = await asyncio.to_thread(
                    self.bot.get_updates, offset_id=self._offset_id, limit=100
                )

                if response.get("status") == "INVALID_INPUT":
                    logging.warning("Invalid offset, resetting to empty.")
                    self._offset_id = ""
                    await asyncio.sleep(poll_interval)
                    continue

                data = response.get("data", {})
                updates_raw = data.get("updates", [])
                next_offset = data.get("next_offset_id")

                for raw_update in updates_raw:
                    try:
                        update = Update(raw_update)
                    except (TypeError, ValueError, AttributeError) as error:
                        logging.error("Could not parse update: %s", error, exc_info=True)
                        continue
                    await self._process_update(update)

                if next_offset:
                    self._offset_id = next_offset

                await asyncio.sleep(poll_interval)

            except Exception as error:
                logging.error("Polling error: %s", error, exc_info=True)
                await asyncio.sleep(5)

    def stop(self):
        self._running = False
