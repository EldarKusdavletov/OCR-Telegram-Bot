from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.future import select

from bot.db.session import async_session, log_user, log_command
from bot.db.models import User, CommandLog, OCRLog

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "stats")

    async with async_session() as session:
        user_id = message.from_user.id

        user_result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        cmd_result = await session.execute(
            select(CommandLog).where(CommandLog.user_id == user_id)
        )
        total_commands = len(cmd_result.scalars().all())  # TODO: inefficient for large tables

        ocr_result = await session.execute(
            select(OCRLog).where(OCRLog.user_id == user_id)
        )
        ocr_logs = ocr_result.scalars().all()
        total_ocr = len(ocr_logs)
        successful_ocr = sum(1 for log in ocr_logs if log.success)

        confidences = [log.confidence for log in ocr_logs if log.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        stats_text = (
            f"📊 <b>Your Statistics:</b>\n\n"
            f"👤 Member since: {user.first_seen.strftime('%Y-%m-%d') if user else 'Unknown'}\n"
            f"🕐 Last activity: {user.last_seen.strftime('%Y-%m-%d %H:%M') if user else 'Unknown'}\n\n"
            f"📝 Commands used: {total_commands}\n"
            f"📸 Photos processed: {total_ocr}\n"
            f"✅ Successful OCR: {successful_ocr}\n"
            f"📊 Average confidence: {avg_confidence:.2%}"
        )

        await message.answer(stats_text, parse_mode="HTML")
