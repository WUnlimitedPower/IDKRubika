import asyncio
import logging
import os

from idk_rubika import (
    Application,
    CommandHandler,
    EventHandler,
    EventTypeEnum,
    MessageHandler,
    UpdateHandler,
    UpdateTypeEnum,
    filters,
)
from idk_rubika.example_handlers import (
    echo_handler,
    on_bot_joined,
    on_bot_removed,
    on_message_edited,
    on_message_removed,
    start_handler,
    delete_handler
)


def main():
    token = os.getenv("RUBIKA_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Rubika token not found. Set the RUBIKA_TOKEN environment variable first."
        )

    app = Application(token,True)

    # Message handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("delete", delete_handler))
    app.add_handler(
        MessageHandler(filters.text & ~filters.command(["start","delete"]), echo_handler)
    )

    # Event handlers
    app.add_handler(EventHandler(EventTypeEnum.BotJoined, on_bot_joined))
    app.add_handler(EventHandler(EventTypeEnum.BotRemoved, on_bot_removed))

    # Update handlers
    app.add_handler(UpdateHandler(UpdateTypeEnum.UpdatedMessage, on_message_edited))
    app.add_handler(UpdateHandler(UpdateTypeEnum.RemovedMessage, on_message_removed))

    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    try:
        main()
    except KeyboardInterrupt:
        print("Bot stopped.")
