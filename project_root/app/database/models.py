from sqlalchemy import Column, BigInteger, String, DateTime
from app.database.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    client_type = Column(String(50), nullable=False)
    date_joined = Column(DateTime, default=datetime.utcnow, nullable=False)
