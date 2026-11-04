
import asyncio
import logging

from idk_rubika import (
    Application,
    CommandHandler,
    MessageHandler,
    EventHandler,
    UpdateHandler,
    filters,
    Keypad,
    KeypadRow,
    Button,
    EventTypeEnum,
    UpdateTypeEnum,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------------------------------------------------------
# دکمه‌های منوی تست
# ---------------------------------------------------------

def build_main_menu() -> Keypad:
    rows = [
        KeypadRow([Button({"id": "btn_chat", "type": "Simple", "button_text": "📋 getChat"})]),
        KeypadRow([Button({"id": "btn_poll", "type": "Simple", "button_text": "📊 sendPoll"})]),
        KeypadRow([Button({"id": "btn_loc", "type": "Simple", "button_text": "📍 sendLocation"})]),
        KeypadRow([Button({"id": "btn_contact", "type": "Simple", "button_text": "👤 sendContact"})]),
        KeypadRow([Button({"id": "btn_keypad", "type": "Simple", "button_text": "⌨️ sendChatKeypad"})]),
        KeypadRow([Button({"id": "btn_inline", "type": "Simple", "button_text": "💠 Inline Keypad"})]),
        KeypadRow([Button({"id": "btn_photo", "type": "Simple", "button_text": "🖼 sendPhoto"})]),
        KeypadRow([Button({"id": "btn_video", "type": "Simple", "button_text": "🎬 sendVideo"})]),
        KeypadRow([Button({"id": "btn_voice", "type": "Simple", "button_text": "🎙 sendVoice"})]),
        KeypadRow([Button({"id": "btn_music", "type": "Simple", "button_text": "🎵 sendMusic"})]),
        KeypadRow([Button({"id": "btn_gif", "type": "Simple", "button_text": "🎞 sendGif"})]),
        KeypadRow([Button({"id": "btn_doc", "type": "Simple", "button_text": "📎 sendDocument"})]),
        KeypadRow([Button({"id": "btn_edit", "type": "Simple", "button_text": "✏️ editMessageText"})]),
        KeypadRow([Button({"id": "btn_delete", "type": "Simple", "button_text": "🗑 deleteMessage"})]),
        KeypadRow([Button({"id": "btn_forward", "type": "Simple", "button_text": "↪️ forwardMessage"})]),
        KeypadRow([Button({"id": "btn_file", "type": "Simple", "button_text": "📥 getFile"})]),
    ]
    return Keypad({"rows": [
        {"buttons": [{"id": b.id, "type": b.type, "button_text": b.button_text} for b in r.buttons]}
        for r in rows
    ]})


# ---------------------------------------------------------
# دستور /start
# ---------------------------------------------------------

async def cmd_start(update, context):
    bot_info = context.bot.get_me()
    await context.bot.send_message(
        chat_id=update.chat_id,
        text=(
            f"سلام! من @{bot_info.username} هستم.\n"
            f"شناسه: {bot_info.bot_id}\n\n"
            "از منوی زیر یک متد را تست کنید:"
        ),
        chat_keypad_type="New",
        chat_keypad=build_main_menu(),
    )


# ---------------------------------------------------------
# هندلر دکمه‌های منوی اصلی
# ---------------------------------------------------------

async def handle_button(update, context):
    if not update.new_message or not update.new_message.aux_data:
        return
    button_id = update.new_message.aux_data.button_id
    chat_id = update.chat_id
    bot = context.bot

    if button_id == "btn_chat":
        chat = await bot.get_chat(chat_id)
        await bot.send_message(
            chat_id=chat_id,
            text=f"getChat:\nchat_id={chat.chat_id}\ntype={chat.chat_type}\ntitle={chat.title}\nusername={chat.username}",
        )

    elif button_id == "btn_poll":
        await bot.send_poll(
            chat_id=chat_id,
            question="نظرسنجی تستی — کدام را دوست داری؟",
            options=["گزینه ۱", "گزینه ۲", "گزینه ۳"],
        )

    elif button_id == "btn_loc":
        await bot.send_location(
            chat_id=chat_id,
            latitude="35.759662741892626",
            longitude="51.4036344416759",
        )

    elif button_id == "btn_contact":
        await bot.send_contact(
            chat_id=chat_id,
            first_name="علی",
            last_name="رضایی",
            phone_number="09123456789",
        )

    elif button_id == "btn_keypad":
        keypad = Keypad({"rows": [
            {"buttons": [{"id": "k1", "type": "Simple", "button_text": "دکمه ۱"}]},
            {"buttons": [{"id": "k2", "type": "Simple", "button_text": "دکمه ۲"}]},
        ]})
        await bot.send_message(
            chat_id=chat_id,
            text="این یک Chat Keypad است.",
            chat_keypad_type="New",
            chat_keypad=keypad,
        )

    elif button_id == "btn_inline":
        inline_keypad = Keypad({"rows": [
            {"buttons": [{"id": "i1", "type": "Simple", "button_text": "Inline ۱"}]},
            {"buttons": [{"id": "i2", "type": "Simple", "button_text": "Inline ۲"}]},
        ]})
        await bot.send_message(
            chat_id=chat_id,
            text="این یک Inline Keypad است.",
            inline_keypad=inline_keypad,
        )

    elif button_id == "btn_photo":
        await bot.send_photo(chat_id, "assets/sample.jpg", caption="عکس تستی")

    elif button_id == "btn_video":
        await bot.send_video(chat_id, "assets/sample.mp4", caption="ویدیو تستی")

    elif button_id == "btn_voice":
        await bot.send_voice(chat_id, "assets/sample.mp3", caption="ویس تستی")

    elif button_id == "btn_music":
        await bot.send_music(chat_id, "assets/sample.mp3", caption="موزیک تستی")

    elif button_id == "btn_gif":
        await bot.send_gif(chat_id, "assets/sample.gif.mp4", caption="گیف تستی")

    elif button_id == "btn_doc":
        await bot.send_document(chat_id, "assets/sample.pdf", caption="فایل تستی")

    elif button_id == "btn_edit":
        sent = await bot.send_message(chat_id=chat_id, text="متن اولیه — در حال ویرایش...")
        if sent:
            await asyncio.sleep(2)
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=sent.message_id,
                text="✅ متن ویرایش شد!",
            )

    elif button_id == "btn_delete":
        sent = await bot.send_message(chat_id=chat_id, text="این پیام ۲ ثانیه بعد حذف می‌شود.")
        if sent:
            await asyncio.sleep(2)
            await bot.delete_message(chat_id=chat_id, message_id=sent.message_id)

    elif button_id == "btn_forward":
        sent = await bot.send_message(chat_id=chat_id, text="این پیام به خودت فوروارد می‌شود.")
        if sent:
            await bot.forward_message(
                from_chat_id=chat_id,
                message_id=sent.message_id,
                to_chat_id=chat_id,
            )

    elif button_id == "btn_file":
        await bot.send_message(chat_id=chat_id, text="برای تست getFile یک فایل بفرستید.")


# ---------------------------------------------------------
# هندلر فایل‌ها (برای تست getFile)
# ---------------------------------------------------------

async def handle_file(update, context):
    msg = update.new_message
    if not msg or not msg.file:
        return
    file_info = await context.bot.get_file(msg.file.file_id)
    if file_info:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text=f"getFile → file_id={file_info.file_id}",
        )


# ---------------------------------------------------------
# هندلرهای Event و Update
# ---------------------------------------------------------

async def on_bot_joined(update, context):
    logging.info("Bot joined chat %s", update.chat_id)
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="ممنون که منو اضافه کردید! /start را بزنید.",
    )

async def on_bot_removed(update, context):
    logging.info("Bot removed from chat %s", update.chat_id)

async def on_message_edited(update, context):
    logging.info("Message edited in chat %s", update.chat_id)

async def on_message_removed(update, context):
    logging.info("Message %s removed in chat %s", update.removed_message_id, update.chat_id)


# ---------------------------------------------------------
# main
# ---------------------------------------------------------

async def main():
    app = Application("YOUR_BOT_TOKEN")

    # دستورات
    app.add_handler(CommandHandler("start", cmd_start))

    # دکمه‌های منو
    app.add_handler(MessageHandler(filters.text & ~filters.command("start"), handle_button))

    # فایل‌ها (getFile)
    app.add_handler(MessageHandler(filters.new_message & ~filters.text, handle_file))

    # رویدادها
    app.add_handler(EventHandler(EventTypeEnum.BotJoined, on_bot_joined))
    app.add_handler(EventHandler(EventTypeEnum.BotRemoved, on_bot_removed))

    # آپدیت‌ها
    app.add_handler(UpdateHandler(UpdateTypeEnum.UpdatedMessage, on_message_edited))
    app.add_handler(UpdateHandler(UpdateTypeEnum.RemovedMessage, on_message_removed))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())