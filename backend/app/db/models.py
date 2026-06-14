from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    conversations = relationship("Conversation", back_populates="user")
    uploaded_files = relationship("UploadedFile", back_populates="user")

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    age = Column(Integer, nullable=True)
    occupation = Column(String, nullable=True)
    income_type = Column(String, nullable=True) # e.g. fixed, variable, seasonal
    income = Column(Float, nullable=True)
    expenses = Column(Float, nullable=True)
    debt = Column(Float, nullable=True)
    goals = Column(Text, nullable=True)
    risk_tolerance = Column(String, nullable=True) # Low, Medium, High
    special_circumstances = Column(Text, nullable=True) # e.g. disability, severe debt
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    conversation = relationship("Conversation", back_populates="profile")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True, default="New Conversation")
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    uploaded_files = relationship("UploadedFile", back_populates="conversation")
    profile = relationship("FinancialProfile", back_populates="conversation", uselist=False)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    conversation = relationship("Conversation", back_populates="messages")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    s3_url = Column(String, nullable=True) # Or local path for dev
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="uploaded_files")
    conversation = relationship("Conversation", back_populates="uploaded_files")
