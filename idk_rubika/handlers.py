from typing import Awaitable, Callable, Optional

from .context import Context
from .enums import EventTypeEnum, UpdateTypeEnum
from .filters import BaseFilter, filters
from .models import Update


class Handler:
    def __init__(
        self,
        callback: Callable[[Update, Context], Awaitable[None]],
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

class CommandTextHandler(MessageHandler):
    """
    مثل CommandHandler، ولی بدون اسلش.
    متنی که دقیقاً برابر با command باشه (بعد از strip) رو match می‌کنه.
    مثال: CommandTextHandler("منو", handler) → وقتی کاربر "منو" بفرسته، handler اجرا می‌شه.
    """

    def __init__(self, command: str | list[str], callback, case_sensitive: bool = False):
        if isinstance(command, str):
            command = [command]
        if case_sensitive:
            self._commands = set(command)
        else:
            self._commands = {c.strip().lower() for c in command}
        self._case_sensitive = case_sensitive
        super().__init__(self._build_filter(), callback)

    def _build_filter(self) -> BaseFilter:
        commands = self._commands
        case_sensitive = self._case_sensitive

        class _TextCommandFilter(BaseFilter):
            def __call__(self, update: Update) -> bool:
                if not update.new_message or not update.new_message.text:
                    return False
                text = update.new_message.text.strip()
                if not case_sensitive:
                    text = text.lower()
                return text in commands

        return _TextCommandFilter()