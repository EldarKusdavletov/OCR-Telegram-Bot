import logging
from datetime import datetime
from aiogram import Bot, F, Router, types

from bot.db.session import log_user, log_ocr
from bot.services.ocr_client import process_image_with_ocr

router = Router()


@router.message(F.photo)
async def handle_photo(message: types.Message, bot: Bot):
    start_time = datetime.utcnow()
    await log_user(message.from_user)

    processing_msg = await message.answer("🔍 Processing image with OCR...")

    photo = message.photo[-1]

    try:
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)

        result = process_image_with_ocr(file_bytes)

        ocr_text = result.get("text", "")
        confidence = result.get("confidence", 0)
        num_pages = result.get("numBilledPages", 0)
        processing_time = (datetime.utcnow() - start_time).total_seconds()

        await log_ocr(
            user_id=message.from_user.id,
            message_id=message.message_id,
            photo_file_id=photo.file_id,
            ocr_text=ocr_text,
            confidence=confidence,
            num_pages=num_pages,
            processing_time=processing_time,
            success=True
        )

        await processing_msg.delete()

        if ocr_text and ocr_text.strip():
            response_text = f"📄 <b>OCR Result:</b>\n\n{ocr_text}\n\n"
            response_text += f"📊 Confidence: {confidence:.2%}\n"
            response_text += f"📄 Pages: {num_pages}\n"
            response_text += f"⏱ Processing time: {processing_time:.2f}s"
            await message.answer(response_text, parse_mode="HTML")
        else:
            await message.answer("⚠️ No text detected in the image.")

    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        error_msg = str(e)
        logging.error(f"Error processing photo for user {message.from_user.id}: {error_msg}")

        await log_ocr(
            user_id=message.from_user.id,
            message_id=message.message_id,
            photo_file_id=photo.file_id,
            processing_time=processing_time,
            success=False,
            error=error_msg
        )

        await processing_msg.delete()
        await message.answer(
            f"❌ An error occurred while processing the image.\n"
            f"<code>{error_msg}</code>", parse_mode="HTML"
        )
