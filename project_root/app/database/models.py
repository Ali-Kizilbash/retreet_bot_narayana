from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # ID пользователя из Telegram
    name = Column(String, nullable=True)   # Имя пользователя
    username = Column(String, unique=True, nullable=True)  # Никнейм пользователя (может быть пустым)
    client_type = Column(String, nullable=False, default="individual")  # Тип клиента
    date_joined = Column(DateTime, nullable=False, default=datetime.utcnow)  # Дата подписки
