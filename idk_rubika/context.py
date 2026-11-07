from typing import Any, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from .bot import RubikaBot


class Context:
    from .models import Update
    def __init__(self, bot: "RubikaBot", update: Update):
        self.bot = bot
        self.update = update
        self.user_data: Dict[str, Any] = {}
        self.chat_data: Dict[str, Any] = {}
