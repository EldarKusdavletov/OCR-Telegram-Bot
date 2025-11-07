from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    first_seen = Column(DateTime, default=datetime.now(UTC))
    last_seen = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))


class OCRLog(Base):
    __tablename__ = "ocr_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now(UTC))
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
    timestamp = Column(DateTime, default=datetime.now(UTC))
    user_id = Column(Integer)
    command = Column(String(100))
