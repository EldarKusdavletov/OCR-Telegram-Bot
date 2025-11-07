from aiogram import Router, types
from aiogram.filters import Command

from bot.db.session import log_user, log_command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "start")

    await message.answer(
        f"👋 Hello, {message.from_user.first_name}!\n"
        f"I'm a simple bot. Try these commands:\n\n"
        f"/start - Start the bot\n"
        f"/help - Show help\n"
        f"/info - Get your info\n"
        f"/stats - Get your usage stats\n\n"
        f"Send me a photo to run OCR!"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "help")

    await message.answer(
        "ℹ️ <b>Available commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/info - Display your Telegram info\n"
        "/stats - Get your usage stats\n\n"
        "You can also send me a photo and I'll read the text from it.",
        parse_mode="HTML"
    )


@router.message(Command("info"))
async def cmd_info(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "info")

    user = message.from_user
    info_text = (
        f"📊 <b>Your Info:</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Username: @{user.username or 'N/A'}\n"
        f"📝 First Name: {user.first_name}\n"
        f"📝 Last Name: {user.last_name or 'N/A'}\n"
        f"🌐 Language: {user.language_code or 'N/A'}"
    )
    await message.answer(info_text, parse_mode="HTML")
