from .enums import EventTypeEnum, UpdateTypeEnum
from .models import Update


class BaseFilter:
    def __call__(self, update: Update) -> bool:
        raise NotImplementedError

    def __and__(self, other: "BaseFilter") -> "BaseFilter":
        return AndFilter(self, other)

    def __or__(self, other: "BaseFilter") -> "BaseFilter":
        return OrFilter(self, other)

    def __invert__(self) -> "BaseFilter":
        return InvertFilter(self)


class AndFilter(BaseFilter):
    def __init__(self, f1: BaseFilter, f2: BaseFilter):
        self.f1, self.f2 = f1, f2

    def __call__(self, update: Update) -> bool:
        return self.f1(update) and self.f2(update)


class OrFilter(BaseFilter):
    def __init__(self, f1: BaseFilter, f2: BaseFilter):
        self.f1, self.f2 = f1, f2

    def __call__(self, update: Update) -> bool:
        return self.f1(update) or self.f2(update)


class InvertFilter(BaseFilter):
    def __init__(self, filter_: BaseFilter):
        self.filter = filter_

    def __call__(self, update: Update) -> bool:
        return not self.filter(update)


class filters:
    class _Text(BaseFilter):
        def __call__(self, update: Update) -> bool:
            return update.new_message is not None and bool(update.new_message.text)

    text = _Text()

    class _NewMessage(BaseFilter):
        def __call__(self, update: Update) -> bool:
            return update.type == UpdateTypeEnum.NewMessage

    new_message = _NewMessage()

    class _Command(BaseFilter):
        def __init__(self, commands):
            if isinstance(commands, str):
                commands = [commands]
            self.commands = {
                command if command.startswith("/") else f"/{command}"
                for command in commands
            }

        def __call__(self, update: Update) -> bool:
            if update.new_message is None or not update.new_message.text:
                return False

            # Only inspect the first token so /start-extra does not match /start.
            command = update.new_message.text.strip().split(maxsplit=1)[0]
            command = command.split("@", maxsplit=1)[0]
            return command in self.commands

    @staticmethod
    def command(commands) -> BaseFilter:
        return filters._Command(commands)

    class _UpdateType(BaseFilter):
        def __init__(self, update_type: UpdateTypeEnum):
            self.update_type = update_type

        def __call__(self, update: Update) -> bool:
            return update.type == self.update_type

    @staticmethod
    def update_type(t: UpdateTypeEnum) -> BaseFilter:
        return filters._UpdateType(t)

    class _EventType(BaseFilter):
        def __init__(self, event_type: EventTypeEnum):
            self.event_type = event_type

        def __call__(self, update: Update) -> bool:
            return (
                update.event_data is not None
                and update.event_data.type == self.event_type
            )

    @staticmethod
    def event_type(t: EventTypeEnum) -> BaseFilter:
        return filters._EventType(t)

    edited_message = _UpdateType(UpdateTypeEnum.UpdatedMessage)
    removed_message = _UpdateType(UpdateTypeEnum.RemovedMessage)
    started_bot = _UpdateType(UpdateTypeEnum.StartedBot)
    stopped_bot = _UpdateType(UpdateTypeEnum.StoppedBot)
    event_data = _UpdateType(UpdateTypeEnum.EventData)
