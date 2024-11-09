from app.database.models import User  # Модель пользователя, которая должна быть определена
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Условие для тестирования
TESTING = True  # Поставьте False, когда хотите снова подключить базу данных


async def user_is_registered(user_id: int, session: AsyncSession) -> bool:
    """Проверяет, зарегистрирован ли пользователь."""
    if TESTING:
        print(f"Тестовый режим: проверка регистрации пользователя {user_id}")
        return False  # Предположим, что пользователь не зарегистрирован
    result = await session.execute(select(User).filter_by(id=user_id))
    return result.scalar_one_or_none() is not None


async def register_user(user_id: int, session: AsyncSession):
    """Регистрирует нового пользователя."""
    if TESTING:
        print(f"Тестовый режим: регистрация пользователя {user_id}")
        return  # Пропускаем добавление пользователя в базу
    new_user = User(id=user_id)
    session.add(new_user)
    await session.commit()


async def get_subscriber_stats():
    # Заглушка для функции, которая должна возвращать статистику подписчиков
    # Временно возвращаем фиктивные данные для тестирования
    print("Тестовый вызов функции get_subscriber_stats")
    return {
        "total_subscribers": 0,
        "active_subscribers": 0
    }

