from typing import Any, Dict, TYPE_CHECKING

from .models import Update

if TYPE_CHECKING:
    from .bot import RubikaBot


class CallbackContext:
    def __init__(self, bot: "RubikaBot", update: Update):
        self.bot = bot
        self.update = update
        self.user_data: Dict[str, Any] = {}
        self.chat_data: Dict[str, Any] = {}
