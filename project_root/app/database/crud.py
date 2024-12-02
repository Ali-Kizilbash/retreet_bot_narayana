from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from datetime import datetime, timedelta

async def add_user(user_id: int, name: str, username: str, client_type: str, session: AsyncSession):
    """
    Добавляет нового пользователя в базу данных.
    """
    new_user = User(
        id=user_id,
        name=name,
        username=username,
        client_type=client_type
    )
    session.add(new_user)
    await session.commit()
    print(f"Пользователь {user_id} добавлен в базу данных.")


async def update_user_type(user_id: int, client_type: str, session: AsyncSession):
    """
    Обновляет тип клиента в базе данных.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.client_type = client_type
        await session.commit()
        print(f"Тип клиента пользователя {user_id} обновлён на {client_type}.")
    else:
        print(f"Пользователь {user_id} не найден в базе данных.")


async def get_user(user_id: int, session: AsyncSession):
    """
    Возвращает пользователя из базы данных.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def user_is_registered(user_id: int, session: AsyncSession) -> bool:
    """
    Проверяет, зарегистрирован ли пользователь в базе данных.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none() is not None


async def get_subscriber_stats(period: str, session: AsyncSession):
    """
    Возвращает количество подписчиков за указанный период.
    - period: "today", "week", "month", "quarter", "half_year", "year", "all".
    """
    now = datetime.utcnow()

    if period == "today":
        # Подписчики за сегодня
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        # Подписчики за последнюю неделю
        start_date = now - timedelta(days=7)
    elif period == "month":
        # Подписчики за последний месяц
        start_date = now.replace(day=1)
    elif period == "quarter":
        # Подписчики за последний квартал (3 месяца)
        start_month = (now.month - 1) // 3 * 3 + 1
        start_date = now.replace(month=start_month, day=1)
    elif period == "half_year":
        # Подписчики за последние 6 месяцев
        start_month = (now.month - 1) // 6 * 6 + 1
        start_date = now.replace(month=start_month, day=1)
    elif period == "year":
        # Подписчики за последний год
        start_date = now.replace(month=1, day=1)
    elif period == "all":
        # Общее количество подписчиков (все пользователи)
        result = await session.execute(select(User))
        return len(result.scalars().all())
    else:
        raise ValueError("Invalid period specified. Use 'today', 'week', 'month', 'quarter', 'half_year', 'year', or 'all'.")

    # Запрос на выборку подписчиков за указанный период
    result = await session.execute(
        select(User).where(User.date_joined >= start_date)
    )
    return len(result.scalars().all())
