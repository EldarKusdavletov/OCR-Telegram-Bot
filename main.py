import asyncio
import logging
import requests
import os

from datetime import datetime, UTC

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not UPSTAGE_API_KEY or not BOT_TOKEN:
    raise ValueError("Make sure you updated your .env file.")

OCR_API_URL = "https://api.upstage.ai/v1/document-digitization"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

DATABASE_URL = "sqlite+aiosqlite:///bot_logs.db"
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OCRLog(Base):
    __tablename__ = "ocr_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer)
    message_id = Column(Integer)
    photo_file_id = Column(String(255))
    ocr_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    num_pages = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    error = Column(Text, nullable=True)


class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer)
    command = Column(String(100))


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized")


async def log_user(user: types.User):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.last_seen = datetime.now(UTC)
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
        else:
            db_user = User(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            session.add(db_user)

        await session.commit()


async def log_command(user_id: int, command: str):
    async with async_session() as session:
        log = CommandLog(user_id=user_id, command=command)
        session.add(log)
        await session.commit()


async def log_ocr(user_id: int, message_id: int, photo_file_id: str,
                  ocr_text: str = None, confidence: float = None,
                  num_pages: int = None, processing_time: float = None,
                  success: bool = False, error: str = None):
    async with async_session() as session:
        log = OCRLog(
            user_id=user_id,
            message_id=message_id,
            photo_file_id=photo_file_id,
            ocr_text=ocr_text,
            confidence=confidence,
            num_pages=num_pages,
            processing_time=processing_time,
            success=success,
            error=error
        )
        session.add(log)
        await session.commit()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "start")

    await message.answer(
        f"👋 Hello, {message.from_user.first_name}!\n"
        f"I'm a simple bot. Try these commands:\n\n"
        f"/start - Start the bot\n"
        f"/help - Show help\n"
        f"/info - Get your info"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await log_user(message.from_user)
    await log_command(message.from_user.id, "help")

    await message.answer(
        "ℹ️ <b>Available commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/info - Display your Telegram info\n\n"
        "You can also send me any text and I'll echo it back!",
        parse_mode="HTML"
    )


@dp.message(Command("info"))
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


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Handle /stats command - show user statistics"""
    await log_user(message.from_user)
    await log_command(message.from_user.id, "stats")

    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.user_id == message.from_user.id)
        )
        user = user_result.scalar_one_or_none()

        cmd_result = await session.execute(
            select(CommandLog).where(CommandLog.user_id == message.from_user.id)
        )
        total_commands = len(cmd_result.scalars().all())

        ocr_result = await session.execute(
            select(OCRLog).where(OCRLog.user_id == message.from_user.id)
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


@dp.message(F.text)
async def echo_text(message: types.Message):
    await log_user(message.from_user)
    await message.answer(f"You said: {message.text}")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    start_time = datetime.now(UTC)
    await log_user(message.from_user)

    processing_msg = await message.answer("🔍 Processing image with OCR...")

    photo = message.photo[-1]
    file = await bot.download(photo)

    try:
        headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
        files = {"document": ("image.jpg", file, "image/jpeg")}
        data = {"model": "ocr"}

        response = requests.post(OCR_API_URL, headers=headers, files=files, data=data)

        if response.status_code == 200:
            result = response.json()

            ocr_text = result.get("text", "")
            confidence = result.get("confidence", 0)
            num_pages = result.get("numBilledPages", 0)

            processing_time = (datetime.now(UTC) - start_time).total_seconds()

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
        else:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"API Error {response.status_code}: {response.text}"

            await log_ocr(
                user_id=message.from_user.id,
                message_id=message.message_id,
                photo_file_id=photo.file_id,
                processing_time=processing_time,
                success=False,
                error=error_msg
            )

            await processing_msg.delete()
            await message.answer(f"❌ OCR API Error: {response.status_code}")

    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logging.error(f"Error processing photo: {e}")

        await log_ocr(
            user_id=message.from_user.id,
            message_id=message.message_id,
            photo_file_id=photo.file_id if 'photo' in locals() else None,
            processing_time=processing_time,
            success=False,
            error=str(e)
        )

        await message.answer(f"❌ Error: {str(e)}")


@dp.message(F.sticker)
async def handle_sticker(message: types.Message):
    await log_user(message.from_user)
    await message.answer("Cool sticker! 😎")


async def main():
    await init_db()
    logging.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
