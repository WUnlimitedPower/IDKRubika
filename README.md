# Rubika Bot Some Codes for C+V in Projects
## فقط یسری کد برای کپی پیسته 
### In Python

یکم کد برای ساخت بات در پیام‌رسان **روبیکا**، با الهام از `python-telegram-bot`. تمام متدهای رسمی [Rubika Bot API](https://rubika.ir/botapi) پوشش داده شده‌اند و خروجی متدها به‌جای `dict` خام، مدل‌های تایپ‌شده (مثل `Message`، `Chat`، `Update`، `File`) هستند.

## ویژگی‌ها

- ✅ پوشش کامل متدهای Rubika Bot API (`sendMessage`, `sendPoll`, `sendFile`, `getChat` و...)
- ✅ مدل‌های تایپ‌شده برای همه‌ی موجودیت‌ها (`Update`, `Message`, `Chat`, `Bot`, `Keypad`, `Metadata` و...)
- ✅ سیستم Handler و Filter به سبک `python-telegram-bot` (`CommandHandler`, `MessageHandler`, `EventHandler`, `UpdateHandler`)
- ✅ Polling با ذخیره‌ی خودکار `offset_id` بر اساس `username` بات (بدون ذخیره‌ی توکن)
- ✅ ارسال فایل دو مرحله‌ای (`requestSendFile` → upload → `sendFile`) با توابع آماده (`send_photo`, `send_video`, `send_voice`, `send_music`, `send_gif`, `send_document`)
- ✅ پشتیبانی از `asyncio`

## نصب

```bash
pip install requests
```

سپس سورس فریم‌ورک را در پروژه‌ی خود کپی کنید (پوشه‌ی `rubika_bot/`).

## ساختار پروژه

```
rubika_bot/
├── __init__.py
├── application.py    # Application (مدیریت polling و handlerها) 
├── bot.py            # کلاس RubikaBot و متدهای API
├── context.py        # CallbackContext
├── database.py       # شاید دیلیتش کنیم( شاید )
├── enums.py          # همه‌ی Enumها (UpdateTypeEnum, ButtonTypeEnum, ...)
├── example_handlers.py # یه چند تا مثال از هندلر ها
├── filters.py        # فیلترها (text, command, update_type, ...)
├── handlers.py       # Handler, MessageHandler, CommandHandler, ...
├── models.py         # مدل‌های داده (Update, Message, Chat, ...)
└── storage.py        # OffsetStore (ذخیره‌ی offset_id)
```

## شروع سریع

- خیلی سریع*

```python
import asyncio
import logging
from rubika_bot import Application, CommandHandler, MessageHandler, filters

async def start(update, context):
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="سلام! به بات خوش آمدید."
    )

async def echo(update, context):
    if update.new_message and update.new_message.text:
        await context.bot.send_message(
            chat_id=update.chat_id,
            text=f"شما گفتید: {update.new_message.text}"
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    app = Application("YOUR_BOT_TOKEN")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.text & ~filters.command("start"), echo))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

## نمونه‌ی تست همه‌ی متدها

یک پوشه به اسم `test_bot/` بسازید و فایل زیر را داخلش بگذارید. این بات با دستور `/start` یک منو نشان می‌دهد که هر دکمه‌اش یک متد API را تست می‌کند.

پوشه‌ی `assets/` را کنار `main.py` بسازید و فایل‌های تستی را داخلش بگذارید:

```
test_bot/
├── main.py
└── assets/
    ├── sample.jpg
    ├── sample.mp4
    ├── sample.mp3
    ├── sample.gif.mp4
    └── sample.pdf
```

> اگر فایل‌های نمونه ندارید، می‌توانید از هر فایل کوچکی با همان پسوند استفاده کنید. فقط حجم‌ها را در نظر بگیرید: عکس حداکثر ۱۰MB، بقیه حداکثر ۵۰MB.

### اجرا

```bash
cd test_bot
python main.py
```

بات ابتدا `getMe` می‌زند، `username` را می‌گیرد، `offsets/{username}.json` را می‌سازد/می‌خواند، و از همان offset شروع به polling می‌کند. با `/start` منوی تست باز می‌شود.

## نکته‌ها

- **توکن ذخیره نمی‌شود.** فقط `offset_id` در `offsets/{username}.json` ذخیره می‌شود.
- **`offsets/` را در `.gitignore` بگذارید.**
- برای وبهوک، از `update_bot_endpoints` استفاده کنید (نیازمند سرور HTTPS عمومی).
- برای مشاهده‌ی همه‌ی مدل‌ها و Enumها، به `rubika_bot/models.py` و `rubika_bot/enums.py` مراجعه کنید.
