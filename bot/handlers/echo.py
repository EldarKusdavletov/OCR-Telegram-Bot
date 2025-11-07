from aiogram import F, Router, types
from bot.db.session import log_user

router = Router()


@router.message(F.text)
async def echo_text(message: types.Message):
    await log_user(message.from_user)
    await message.answer(f"Did you say: \"{message.text}\"?")


@router.message(F.sticker)
async def handle_sticker(message: types.Message):
    await log_user(message.from_user)
    await message.answer("Cool sticker! 😎")
