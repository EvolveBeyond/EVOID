# Telegram Adapter

Telegram bot adapter using aiogram.

## Basic Usage

```python
import asyncio
import os
from evoid.adapters.telegram import create_bot, run_bot
from evoid.core import Intent, Level

# Create bot
bot = create_bot(token=os.environ["TELEGRAM_TOKEN"])

# Register handlers
async def handle_start(intent: Intent) -> str:
    return "Welcome!"

bot.on("command:/start", handle_start)
bot.on("message", lambda i: f"Echo: {i.metadata.get('text', '')}")

# Run
asyncio.run(run_bot(bot))
```

## Requirements

```bash
uv add "evoid[telegram]"
# or
uv add aiogram
```
