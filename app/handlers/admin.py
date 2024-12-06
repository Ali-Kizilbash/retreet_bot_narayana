# admin.py

import os
import logging
from aiogram import Router, Bot, types, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.keyboards.admin_kb import (
    get_admin_menu,
    get_file_management_menu,
    get_subscriber_stats_menu,
)
from app.database.crud import get_subscriber_stats  # Функция для получения статистики
from app.database.db import get_async_session
from app.handlers.common import is_staff  # Функция проверки прав администратора

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("admin_panel"))
async def admin_panel(message: types.Message, state: FSMContext):
    """Команда для отображения админ-панели."""
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    logger.info(f"Команда /admin_panel вызвана пользователем: {username} (user_id: {user_id})")

    # Проверка прав администратора
    if not is_staff(user_id=user_id, username=username):
        logger.warning(f"Пользователь {user_id} ({username}) попытался использовать /admin_panel без прав.")
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    try:
        await message.answer("Добро пожаловать в админ-панель.", reply_markup=get_admin_menu())
        logger.info("Админ-панель успешно отображена.")
    except Exception as e:
        logger.error(f"Ошибка при отображении админ-панели: {e}")
        await message.answer("Произошла ошибка при отображении админ-панели.")


@router.callback_query(lambda c: c.data == "manage_files")
async def manage_files(callback_query: CallbackQuery):
    """Показывает меню управления файлами."""
    logger.info("Вызвано меню управления файлами.")
    try:
        await callback_query.message.answer("Управление файлами и текстами:", reply_markup=get_file_management_menu())
        await callback_query.answer()
        logger.info("Меню управления файлами успешно отображено.")
    except Exception as e:
        logger.error(f"Ошибка при отображении меню управления файлами: {e}")
        await callback_query.message.answer("Произошла ошибка при отображении меню управления файлами.")
        await callback_query.answer()


@router.callback_query(lambda c: c.data == "view_files")
async def view_files(callback_query: CallbackQuery):
    """Отображает список доступных файлов в папке resources."""
    logger.info("Запрос списка файлов в папке resources.")
    try:
        files = os.listdir("resources")
        logger.debug(f"Файлы в папке resources: {files}")
        if files:
            files_text = "\n".join(files)
            await callback_query.message.answer(f"Доступные файлы:\n{files_text}")
        else:
            await callback_query.message.answer("Нет доступных файлов.")
        await callback_query.answer()
        logger.info("Список файлов успешно отправлен пользователю.")
    except FileNotFoundError:
        logger.warning("Папка resources не найдена.")
        await callback_query.message.answer("Папка resources не найдена.")
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Ошибка при отображении списка файлов: {e}")
        await callback_query.message.answer("Произошла ошибка при отображении списка файлов.")
        await callback_query.answer()


@router.callback_query(lambda c: c.data == "subscriber_stats")
async def subscriber_stats_menu(callback_query: CallbackQuery):
    """Отображает меню статистики подписчиков."""
    logger.info("Вызвано меню статистики подписчиков.")
    try:
        await callback_query.message.answer(
            "Выберите интересующий период статистики:",
            reply_markup=get_subscriber_stats_menu()
        )
        await callback_query.answer()
        logger.info("Меню статистики подписчиков успешно отображено.")
    except Exception as e:
        logger.error(f"Ошибка при отображении меню статистики подписчиков: {e}")
        await callback_query.message.answer("Ошибка при отображении меню статистики подписчиков.")
        await callback_query.answer()


@router.callback_query(lambda c: c.data in [
    "current_subscribers",
    "daily_growth",
    "weekly_growth",
    "monthly_growth",
    "quarterly_growth",
    "half_year_growth",
    "yearly_growth"
])
async def subscriber_growth(callback_query: CallbackQuery, bot: Bot):
    """Показывает количество подписчиков за выбранный период."""
    period_map = {
        "current_subscribers": "all",
        "daily_growth": "today",
        "weekly_growth": "week",
        "monthly_growth": "month",
        "quarterly_growth": "quarter",
        "half_year_growth": "half_year",
        "yearly_growth": "year",
    }

    action = callback_query.data
    period = period_map.get(action, "all")
    logger.info(f"Обработчик '{action}' вызван.")

    try:
        session = await get_async_session()
        async with session:
            logger.info(f"Открыта сессия базы данных для статистики за период: {period}.")
            subscriber_count = await get_subscriber_stats(period, session)
            if action == "current_subscribers":
                response_text = f"Общее количество подписчиков: {subscriber_count}"
            elif action == "daily_growth":
                response_text = f"Подписки за сегодня: {subscriber_count}"
            elif action == "weekly_growth":
                response_text = f"Подписки за последнюю неделю: {subscriber_count}"
            elif action == "monthly_growth":
                response_text = f"Подписки за последний месяц: {subscriber_count}"
            elif action == "quarterly_growth":
                response_text = f"Подписки за последний квартал: {subscriber_count}"
            elif action == "half_year_growth":
                response_text = f"Подписки за последние полгода: {subscriber_count}"
            elif action == "yearly_growth":
                response_text = f"Подписки за последний год: {subscriber_count}"
            else:
                response_text = f"Подписчики за период '{period}': {subscriber_count}"

            await callback_query.message.answer(response_text)
            logger.info(f"Статистика за период '{period}' успешно отправлена пользователю.")
    except Exception as e:
        logger.error(f"Ошибка при получении статистики за период '{period}': {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()
