#!/usr/bin/env python3
"""LMS Telegram Bot - Entry point with --test mode."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command string into command and arguments.
    
    Args:
        text: The input text (e.g., "/scores lab-04" or "/start")
    
    Returns:
        Tuple of (command, args)
    """
    text = text.strip()
    if not text:
        return "", ""
    
    parts = text.split(maxsplit=1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args


def dispatch_command(command: str, args: str) -> str:
    """Dispatch a command to the appropriate handler.
    
    Args:
        command: The command name (e.g., "/start", "/help")
        args: Command arguments
    
    Returns:
        Handler response text
    """
    # Normalize command (remove leading slash if present)
    cmd = command.lstrip("/").lower()
    
    handlers = {
        "start": lambda: handle_start(),
        "help": lambda: handle_help(),
        "health": lambda: handle_health(),
        "labs": lambda: handle_labs(),
        "scores": lambda: handle_scores(args),
    }
    
    handler = handlers.get(cmd)
    if handler:
        return handler()
    
    return f"Unknown command: {command}. Use /help to see available commands."


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode and print result to stdout.
    
    Args:
        command_text: The command to test (e.g., "/start" or "/scores lab-04")
    """
    command, args = parse_command(command_text)
    response = dispatch_command(command, args)
    print(response)


async def telegram_handlers(dp: Dispatcher) -> None:
    """Register Telegram message handlers."""
    
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        """Handle /start command."""
        response = handle_start()
        await message.answer(response)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        """Handle /help command."""
        response = handle_help()
        await message.answer(response)
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        """Handle /health command."""
        response = handle_health()
        await message.answer(response)
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        """Handle /labs command."""
        response = handle_labs()
        await message.answer(response)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        """Handle /scores command."""
        args = message.text.split(maxsplit=1)
        lab_id = args[1] if len(args) > 1 else ""
        response = handle_scores(lab_id)
        await message.answer(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    if not settings.bot_token:
        logger.error("BOT_TOKEN not set. Please configure .env.bot.secret")
        return
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    await telegram_handlers(dp)
    
    logger.info("Bot starting...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run a command in test mode (e.g., --test '/start')",
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
