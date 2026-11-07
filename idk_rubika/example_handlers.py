import logging

from .context import Context
from .models import Update


async def start_handler(update: Update, context: Context):
    if update.new_message:
        await update.new_message.reply_photo(
            "start.jpeg",
            "سلام! به بات خوش آمدید."
        )


async def delete_handler(update: Update, context: Context):
    if update.new_message:
        result = await update.new_message.delete()
        if result.deleted:
            logging.info("Message deleted")
        else:
            logging.info("Bot cannot delete the message")


async def echo_handler(update: Update, context: Context):
    if update.new_message and update.new_message.text:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text=f"شما گفتید: {update.new_message.text}",
        )


async def on_bot_joined(update: Update, context: Context):
    logging.info("Bot joined chat: %s", update.chat_id)
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="ممنون که منو اضافه کردید! برای شروع /start رو بزنید.",
    )


async def on_bot_removed(update: Update, context: Context):
    logging.info("Bot removed from chat: %s", update.chat_id)


async def on_message_edited(update: Update, context: Context):
    if update.updated_message:
        logging.info(
            "Message %s edited in %s",
            update.updated_message.message_id,
            update.chat_id,
        )


async def on_message_removed(update: Update, context: Context):
    logging.info("Message %s removed in %s", update.removed_message_id, update.chat_id)
