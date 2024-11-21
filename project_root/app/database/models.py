from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)  # ID Telegram пользователя
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    client_type = Column(String, nullable=False)  # Тип клиента: organizer, individual
    created_at = Column(DateTime, default=datetime.utcnow)