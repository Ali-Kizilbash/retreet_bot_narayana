from app.database.models import User  # Модель пользователя, которая должна быть определена
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def user_is_registered(user_id: int, session: AsyncSession) -> bool:
    """Проверяет, зарегистрирован ли пользователь."""
    result = await session.execute(select(User).filter_by(id=user_id))
    return result.scalar_one_or_none() is not None


async def register_user(user_id: int, session: AsyncSession):
    """Регистрирует нового пользователя."""
    new_user = User(id=user_id)
    session.add(new_user)
    await session.commit()
