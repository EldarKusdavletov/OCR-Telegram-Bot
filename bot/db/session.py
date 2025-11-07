import logging
from datetime import datetime
from aiogram import types

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select

from config import DATABASE_URL
from .models import Base, User, CommandLog, OCRLog

# In case if your deployment environment doesn't allow you to change the DATABASE_URL variable
# if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
#     DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def log_user(user: types.User):
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User).where(User.user_id == user.id)
            )
            db_user = result.scalar_one_or_none()

            if db_user:
                db_user.last_seen = datetime.utcnow()
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
            else:
                db_user = User(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    first_seen=datetime.utcnow()  # Ensure first_seen is set
                )
                session.add(db_user)

            await session.commit()
        except Exception as e:
            logging.error(f"Error logging user {user.id}: {e}")
            await session.rollback()


async def log_command(user_id: int, command: str):
    async with async_session() as session:
        try:
            log = CommandLog(user_id=user_id, command=command)
            session.add(log)
            await session.commit()
        except Exception as e:
            logging.error(f"Error logging command '{command}' for user {user_id}: {e}")
            await session.rollback()


async def log_ocr(user_id: int, message_id: int, photo_file_id: str,
                  ocr_text: str = None, confidence: float = None,
                  num_pages: int = None, processing_time: float = None,
                  success: bool = False, error: str = None):
    async with async_session() as session:
        try:
            log = OCRLog(
                user_id=user_id,
                message_id=message_id,
                photo_file_id=photo_file_id,
                ocr_text=ocr_text,
                confidence=confidence,
                num_pages=num_pages,
                processing_time=processing_time,
                success=success,
                error=error,
                timestamp=datetime.utcnow()
            )
            session.add(log)
            await session.commit()
        except Exception as e:
            logging.error(f"Error logging OCR for user {user_id}: {e}")
            await session.rollback()
