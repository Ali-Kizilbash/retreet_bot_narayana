# crud.py

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from datetime import datetime, timedelta

# Вам не нужно изменять этот файл, так как он принимает сессию как параметр
# и логика работы с сессией остается прежней.

async def add_user(user_id: int, name: str, username: str, client_type: str, session: AsyncSession):
    """Добавляет нового пользователя в базу данных."""
    new_user = User(
        id=user_id,
        name=name,
        username=username,
        client_type=client_type,
        date_joined=datetime.utcnow()
    )
    session.add(new_user)
    await session.commit()


async def user_is_registered(user_id: int, session: AsyncSession) -> bool:
    """Проверяет, зарегистрирован ли пользователь в базе данных."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none() is not None


async def update_user_type(user_id: int, client_type: str, session: AsyncSession):
    """Обновляет тип клиента в базе данных."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.client_type = client_type
        await session.commit()


async def get_user(user_id: int, session: AsyncSession):
    """Получает данные пользователя по user_id."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_subscriber_stats(period: str, session: AsyncSession):
    """Возвращает количество подписчиков за указанный период."""
    now = datetime.utcnow()

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now.replace(day=1)
    elif period == "quarter":
        start_month = (now.month - 1) // 3 * 3 + 1
        start_date = now.replace(month=start_month, day=1)
    elif period == "half_year":
        start_month = (now.month - 1) // 6 * 6 + 1
        start_date = now.replace(month=start_month, day=1)
    elif period == "year":
        start_date = now.replace(month=1, day=1)
    elif period == "all":
        result = await session.execute(select(User))
        return len(result.scalars().all())
    else:
        raise ValueError("Invalid period specified.")

    result = await session.execute(select(User).where(User.date_joined >= start_date))
    return len(result.scalars().all())
