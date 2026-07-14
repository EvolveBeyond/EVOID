"""Telegram Bot Example — Intent-based Telegram bot.

This example shows how to create a Telegram bot using EVOID:
1. Define Intents for different commands
2. Create handlers
3. Run the bot

Usage:
    1. Get a bot token from @BotFather
    2. Set token: export TELEGRAM_TOKEN="your_token"
    3. Run: python main.py

Requirements:
    pip install aiogram
"""

import asyncio
import os
from typing import Any

from evoid.core import Intent, Level, register
from evoid.adapters.telegram import create_bot, run_bot
from evoid.engines.logger import loguru as log


# ============================================================
# 1. Define Intents
# ============================================================

START = Intent(
    name="telegram:command:/start",
    level=Level.STANDARD,
)

HELP = Intent(
    name="telegram:command:/help",
    level=Level.STANDARD,
)

ECHO = Intent(
    name="telegram:message",
    level=Level.EPHEMERAL,
)

PAYMENT = Intent(
    name="telegram:command:/pay",
    level=Level.CRITICAL,
)


# ============================================================
# 2. Define Handlers
# ============================================================

async def handle_start(intent: Intent) -> str:
    """Handle /start command."""
    username = intent.metadata.get("username", "User")
    log.info(f"Start command from @{username}")
    return f"Welcome {username}! I'm an EVOID-powered bot."


async def handle_help(intent: Intent) -> str:
    """Handle /help command."""
    log.info("Help command")
    return """
Available commands:
/start - Welcome message
/help - Show this help
/echo <text> - Echo your message
/pay <amount> - Process payment (demo)
"""


async def handle_echo(intent: Intent) -> str:
    """Handle any message as echo."""
    text = intent.metadata.get("text", "")
    log.info(f"Echo: {text}")
    return f"Echo: {text}"


async def handle_pay(intent: Intent) -> str:
    """Handle /pay command."""
    args = intent.metadata.get("args", [])
    amount = args[0] if args else "0"
    log.info(f"Payment command: {amount}")
    return f"Payment of {amount} processed! (demo)"


# ============================================================
# 3. Create and Run Bot
# ============================================================

def main():
    """Run the Telegram bot."""
    # Get token from environment
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("Error: Set TELEGRAM_TOKEN environment variable")
        print("  export TELEGRAM_TOKEN='your_bot_token'")
        return

    # Initialize loguru
    log.init("evoid-telegram", level="INFO")

    # Create bot
    bot = create_bot(token=token)

    # Register handlers
    bot.on("command:/start", handle_start)
    bot.on("command:/help", handle_help)
    bot.on("command:/pay", handle_pay)
    bot.on("message", handle_echo)

    # Run bot
    print("Starting Telegram bot...")
    print("Press Ctrl+C to stop")
    asyncio.run(run_bot(bot))


if __name__ == "__main__":
    main()
