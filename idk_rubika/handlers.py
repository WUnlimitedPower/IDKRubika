from typing import Awaitable, Callable, Optional

from .context import CallbackContext
from .enums import EventTypeEnum, UpdateTypeEnum
from .filters import BaseFilter, filters
from .models import Update


class Handler:
    def __init__(
        self,
        callback: Callable[[Update, CallbackContext], Awaitable[None]],
        filter_: Optional[BaseFilter] = None,
    ):
        self.callback = callback
        self.filter = filter_

    def check(self, update: Update) -> bool:
        if self.filter is None:
            return True
        return self.filter(update)


class MessageHandler(Handler):
    def __init__(self, filter_: BaseFilter, callback):
        super().__init__(callback, filter_)


class CommandHandler(MessageHandler):
    def __init__(self, command, callback):
        super().__init__(filters.command(command), callback)


class EventHandler(Handler):
    def __init__(self, event_type: EventTypeEnum, callback):
        super().__init__(callback, filters.event_type(event_type))


class UpdateHandler(Handler):
    def __init__(self, update_type: UpdateTypeEnum, callback):
        super().__init__(callback, filters.update_type(update_type))
