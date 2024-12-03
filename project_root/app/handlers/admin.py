# admin.py

from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from app.keyboards.admin_kb import (
    get_admin_menu,
    get_file_management_menu,
    get_subscriber_stats_menu,
)
from app.database.crud import get_subscriber_stats  # Функция для получения статистики
from app.database.db import get_async_session
from aiogram.fsm.context import FSMContext
import logging
import os

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("admin_panel"))
async def admin_panel(message: types.Message):
    """Команда для отображения админ-панели."""
    logger.info("Команда /admin_panel вызвана пользователем: %s", message.from_user.username)
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

@router.callback_query(lambda c: c.data == "view_files")
async def view_files(callback_query: CallbackQuery):
    """Отображает список доступных файлов в папке resources."""
    logger.info("Запрос списка файлов в папке resources.")
    try:
        files = os.listdir("resources")
        logger.debug("Файлы в папке resources: %s", files)
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

@router.callback_query(lambda c: c.data == "current_subscribers")
async def current_subscribers(callback_query: CallbackQuery):
    """Показывает общее количество подписчиков."""
    logger.info("Обработчик 'current_subscribers' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для общего количества подписчиков.")
            subscriber_count = await get_subscriber_stats("all", session)
            logger.info(f"Общее количество подписчиков: {subscriber_count}")
            await callback_query.message.answer(f"Общее количество подписчиков: {subscriber_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении общего количества подписчиков: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "daily_growth")
async def daily_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за день."""
    logger.info("Обработчик 'daily_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за день.")
            today_count = await get_subscriber_stats("today", session)
            logger.info(f"Количество подписок за сегодня: {today_count}")
            await callback_query.message.answer(f"Подписки за сегодня: {today_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за день: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "weekly_growth")
async def weekly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за неделю."""
    logger.info("Обработчик 'weekly_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за неделю.")
            weekly_count = await get_subscriber_stats("week", session)
            logger.info(f"Количество подписок за последнюю неделю: {weekly_count}")
            await callback_query.message.answer(f"Подписки за последнюю неделю: {weekly_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за неделю: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "monthly_growth")
async def monthly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за месяц."""
    logger.info("Обработчик 'monthly_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за месяц.")
            monthly_count = await get_subscriber_stats("month", session)
            logger.info(f"Количество подписок за последний месяц: {monthly_count}")
            await callback_query.message.answer(f"Подписки за последний месяц: {monthly_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за месяц: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "quarterly_growth")
async def quarterly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за квартал."""
    logger.info("Обработчик 'quarterly_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за квартал.")
            quarterly_count = await get_subscriber_stats("quarter", session)
            logger.info(f"Количество подписок за последний квартал: {quarterly_count}")
            await callback_query.message.answer(f"Подписки за последний квартал: {quarterly_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за квартал: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "half_year_growth")
async def half_year_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за полгода."""
    logger.info("Обработчик 'half_year_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за полгода.")
            half_year_count = await get_subscriber_stats("half_year", session)
            logger.info(f"Количество подписок за последние полгода: {half_year_count}")
            await callback_query.message.answer(f"Подписки за последние полгода: {half_year_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за полгода: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data == "yearly_growth")
async def yearly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за год."""
    logger.info("Обработчик 'yearly_growth' вызван.")
    try:
        async with get_async_session() as session:
            logger.info("Открыта сессия базы данных для статистики за год.")
            yearly_count = await get_subscriber_stats("year", session)
            logger.info(f"Количество подписок за последний год: {yearly_count}")
            await callback_query.message.answer(f"Подписки за последний год: {yearly_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении количества подписок за год: {e}")
        await callback_query.message.answer("Ошибка при получении статистики.")
    finally:
        await callback_query.answer()
