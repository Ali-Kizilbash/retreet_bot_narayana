from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.models import Client


async def get_client_by_user_id(session: AsyncSession, user_id: int) -> Client:
    """Получает клиента по user_id."""
    result = await session.execute(select(Client).filter_by(user_id=user_id))
    return result.scalar_one_or_none()


async def register_client(session: AsyncSession, user_id: int, first_name: str, last_name: str, client_type: str):
    """Регистрирует нового клиента."""
    try:
        client = Client(user_id=user_id, first_name=first_name, last_name=last_name, client_type=client_type)
        session.add(client)
        await session.commit()
        print(f"[DEBUG] Клиент {user_id} успешно зарегистрирован с типом: {client_type}")
    except Exception as e:
        await session.rollback()
        print(f"[ERROR] Ошибка при регистрации клиента {user_id}: {e}")


async def update_client_type(session: AsyncSession, user_id: int, new_type: str):
    """Обновляет тип клиента."""
    client = await get_client_by_user_id(session, user_id)
    if client:
        client.client_type = new_type
        await session.commit()


async def get_subscriber_stats(session: AsyncSession, stat_type: str) -> int:
    """
    Получает статистику подписчиков по заданному типу.
    :param session: Сессия базы данных.
    :param stat_type: Тип статистики: "current", "daily", "monthly".
    :return: Количество подписчиков.
    """
    if stat_type == "current":
        result = await session.execute(select(func.count()).select_from(Client))
        return result.scalar()

    elif stat_type == "daily":
        yesterday = datetime.utcnow() - timedelta(days=1)
        result = await session.execute(
            select(func.count()).select_from(Client).where(Client.created_at >= yesterday)
        )
        return result.scalar()

    elif stat_type == "monthly":
        last_month = datetime.utcnow() - timedelta(days=30)
        result = await session.execute(
            select(func.count()).select_from(Client).where(Client.created_at >= last_month)
        )
        return result.scalar()

    else:
        raise ValueError("Некорректный тип статистики. Используйте 'current', 'daily' или 'monthly'.")
