"""Telegram Adapter — Converts Telegram messages to Intents.

IOP: Adapter is just functions. No class with behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core.runtime import execute


# Handler type
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class TelegramBot:
    """Telegram bot — pure data (token + handlers)."""

    token: str
    handlers: dict[str, Handler] = field(default_factory=dict)


def create_bot(token: str) -> TelegramBot:
    """Create a Telegram bot."""
    return TelegramBot(token=token)


def on(bot: TelegramBot, event_type: str, handler: Handler) -> None:
    """Register handler for event type."""
    bot.handlers[event_type] = handler


def _intent_from_message(message: Any) -> Intent:
    """Convert aiogram message to Intent."""
    text = message.text or ""
    user = message.from_user

    if text.startswith("/"):
        command = text.split()[0].lstrip("/")
        name = f"telegram:command:{command}"
    else:
        name = "telegram:message"

    return Intent(
        name=name,
        level=Level.STANDARD,
        metadata={
            "text": text,
            "command": text.split()[0] if text.startswith("/") else None,
            "args": text.split()[1:] if text.startswith("/") else [],
            "user_id": user.id if user else None,
            "username": user.username if user else None,
            "chat_id": message.chat.id if message.chat else None,
            "message_id": message.message_id,
        },
    )


async def run_bot(bot: TelegramBot) -> None:
    """Run the Telegram bot."""
    try:
        from aiogram import Bot, Dispatcher
    except ImportError:
        raise ImportError("aiogram required: pip install aiogram")

    _bot = Bot(token=bot.token)
    dp = Dispatcher()

    @dp.message()
    async def message_handler(message: Any) -> None:
        intent = _intent_from_message(message)

        handler = bot.handlers.get("message")

        if intent.metadata.get("command"):
            cmd_handler = bot.handlers.get(f"command:/{intent.metadata['command']}")
            if cmd_handler:
                handler = cmd_handler

        if handler:
            result = await handler(intent)
            if result:
                await message.answer(str(result))
        else:
            pipeline_result = await execute(intent)
            if pipeline_result.success and pipeline_result.value:
                await message.answer(str(pipeline_result.value))

    print(f"Starting Telegram bot...")
    await dp.start_polling(_bot)
