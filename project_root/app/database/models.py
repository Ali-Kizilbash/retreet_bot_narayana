from sqlalchemy.orm import declarative_base
from sqlalchemy import BigInteger, Column, String, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)  # ID пользователя из Telegram
    name = Column(String, nullable=True)               # Имя пользователя
    username = Column(String, nullable=True)           # Никнейм пользователя
    client_type = Column(String, nullable=False, default="individual")  # Тип клиента
    date_joined = Column(DateTime, nullable=False, default=datetime.utcnow)  # Дата регистрации
