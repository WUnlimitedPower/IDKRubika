import logging
from typing import List, Dict, Any, Tuple
from .handlers import Handler
from .models import Update
from .context import Context


class ConversationHandler(Handler):
    END: int = -1
    WAITING: int = -3

    def __init__(
        self,
        entry_points: List[Handler],
        states: Dict[Any, List[Handler]],
        fallbacks: List[Handler],
        allow_reentry: bool = False,
    ):
        async def _placeholder(update, context):
            logging.info("AHsdAHdioahsdoiahsdoiahsdoh")
            return None

        super().__init__(callback=self.callback)
        self.entry_points = entry_points
        self.states = states
        self.fallbacks = fallbacks
        self.allow_reentry = allow_reentry

        # {(chat_id, user_id): {"state": state, "data": dict}}
        self._conversations: Dict[Tuple[str, str], dict] = {}

    @staticmethod
    def _key(update: Update) -> Tuple[str, str]:
        user_id = ""
        if update.new_message:
            user_id = update.new_message.sender_id
        elif update.updated_message:
            user_id = update.updated_message.sender_id
        return (update.chat_id, user_id)

    def check(self, update: Update) -> bool:
        key = self._key(update)
        conv = self._conversations.get(key)

        if conv is None:
            return any(h.check(update) for h in self.entry_points)

        state_handlers = self.states.get(conv["state"], [])
        if any(h.check(update) for h in state_handlers):
            return True

        if any(h.check(update) for h in self.fallbacks):
            return True

        if self.allow_reentry and any(h.check(update) for h in self.entry_points):
            return True

        return False

    async def callback(self, update: Update, context: Context):
        key = self._key(update)
        conv = self._conversations.get(key)

        # شروع یا ری‌استارت
        if conv is None or (
            self.allow_reentry
            and any(h.check(update) for h in self.entry_points)
        ):
            for handler in self.entry_points:
                if handler.check(update):
                    conv = {
                        "state": 0,
                        "data": {},
                    }
                    self._conversations[key] = conv
                    context.user_data = conv["data"]
                    result = await handler.callback(update, context)
                    conv["data"] = context.user_data
                    if result is None or result == self.END:
                        self._conversations.pop(key, None)
                    else:
                        conv["state"] = result
                    return
            return

        # ادامه
        state_handlers = self.states.get(conv["state"], [])

        for handler in state_handlers:
            if handler.check(update):
                context.user_data = conv["data"]
                result = await handler.callback(update, context)
                conv["data"] = context.user_data
                if result == self.END:
                    self._conversations.pop(key, None)
                elif result is not None:
                    conv["state"] = result
                return

        for handler in self.fallbacks:
            if handler.check(update):
                context.user_data = conv["data"]
                result = await handler.callback(update, context)
                conv["data"] = context.user_data
                if result == self.END:
                    self._conversations.pop(key, None)
                elif result is not None:
                    conv["state"] = result
                return