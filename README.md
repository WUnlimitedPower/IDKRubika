# Rubika Bot API Wrapper

A small, modular Python wrapper for the Rubika Bot API. The original public class names, method names, enum names, model attributes, and handler usage are preserved.

## Project structure

```text
idk_rubika_project/
├── main.py
├── requirements.txt
├── README.md
└── idk_rubika/
    ├── __init__.py
    ├── application.py
    ├── bot.py
    ├── context.py
    ├── database.py
    ├── enums.py
    ├── example_handlers.py
    ├── filters.py
    ├── handlers.py
    └── models.py
```

## Install

Python 3.9 or newer is recommended because the polling implementation uses `asyncio.to_thread`.

```bash
python -m pip install -r requirements.txt
```

## Run the example

Set your Rubika bot token as an environment variable; do not put a real token in a public source file.

**Windows CMD:**

```bat
set RUBIKA_TOKEN=YOUR_BOT_TOKEN
python main.py
```

**PowerShell:**

```powershell
$env:RUBIKA_TOKEN = "YOUR_BOT_TOKEN"
python main.py
```

**Linux / macOS:**

```bash
export RUBIKA_TOKEN="YOUR_BOT_TOKEN"
python main.py
```

## Basic usage

```python
from idk_rubika import Application, CommandHandler

async def start_handler(update, context):
    await context.bot.send_message(
        chat_id=update.chat_id,
        text="Hello!",
    )

app = Application("YOUR_BOT_TOKEN")
app.add_handler(CommandHandler("start", start_handler))

# Start polling from an async entry point:
# await app.run_polling()
```

## Included modules

- `enums.py`: API enum values.
- `models.py`: API response models such as `Update`, `Message`, `Button`, and `Keypad`.
- `filters.py`: composable filters using `&`, `|`, and `~`.
- `handlers.py`: message, command, event, and update handlers.
- `context.py`: `CallbackContext` supplied to each callback.
- `bot.py`: methods that call the Rubika Bot API.
- `application.py`: polling loop, update dispatch, and pending-update draining.
- `database.py`: a simple in-memory key/value store. It does **not** persist data after the process exits.
- `example_handlers.py`: handlers used by the included `main.py` example.

## Notes

- Async API methods run the synchronous `requests` calls in a worker thread, so they do not block the event loop while waiting for an HTTP response.
- `_post` raises an exception for HTTP errors and rejects non-object JSON responses. Polling and handler errors are logged.
- `filters.command()` matches the command token itself, so `/start-extra` does not accidentally match `/start`. A command such as `/start@YourBot` matches `/start`.
- The wrapper does not validate every request field against the Rubika API. Check the API documentation for the exact parameters accepted by each endpoint.
