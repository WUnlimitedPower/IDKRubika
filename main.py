import asyncio
import logging
import os
from idk_rubika import Application, CommandHandler, MessageHandler, filters, Update, CallbackContext

async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="سلام! به بات خوش آمدید.",
        reply_id= update.new_message.message_id
        
    )

async def echo(update, context):
    if update.new_message and update.new_message.text:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text=f"شما گفتید: {update.new_message.text}"
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    app = Application(os.getenv("token"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.text & ~filters.command("start"), echo))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())