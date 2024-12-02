from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.filters import Command
import os
from app.keyboards.admin_kb import (get_admin_menu,
                                    get_file_management_menu,
                                    get_subscriber_stats_menu
)
from app.database.crud import get_subscriber_stats # Функция для получения статистики
from app.database.db import get_async_session
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("admin_panel"))
async def admin_panel(message: types.Message):
    """Команда для отображения админ-панели."""
    print("Команда /admin_panel вызвана пользователем:", message.from_user.username)
    try:
        await message.answer("Добро пожаловать в админ-панель.", reply_markup=get_admin_menu())
        print("Админ-панель успешно отображена.")
    except Exception as e:
        print(f"Ошибка при отображении админ-панели: {e}")

@router.callback_query(lambda c: c.data == "manage_files")
async def manage_files(callback_query: CallbackQuery):
    """Показывает меню управления файлами."""
    print("Вызвано меню управления файлами.")
    try:
        await callback_query.message.answer("Управление файлами и текстами:", reply_markup=get_file_management_menu())
        await callback_query.answer()
        print("Меню управления файлами успешно отображено.")
    except Exception as e:
        print(f"Ошибка при отображении меню управления файлами: {e}")

@router.callback_query(lambda c: c.data == "view_files")
async def view_files(callback_query: CallbackQuery):
    """Отображает список доступных файлов в папке resources."""
    print("Запрос списка файлов в папке resources.")
    try:
        files = os.listdir("resources")
        print("Файлы в папке resources:", files)
        if files:
            files_text = "\n".join(files)
            await callback_query.message.answer(f"Доступные файлы:\n{files_text}")
        else:
            await callback_query.message.answer("Нет доступных файлов.")
        await callback_query.answer()
        print("Список файлов успешно отправлен пользователю.")
    except FileNotFoundError:
        print("Папка resources не найдена.")
        await callback_query.message.answer("Папка resources не найдена.")
        await callback_query.answer()
    except Exception as e:
        print(f"Ошибка при отображении списка файлов: {e}")


@router.callback_query(lambda c: c.data == "current_subscribers")
async def current_subscribers(callback_query: CallbackQuery):
    """Показывает общее количество подписчиков."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос общего количества подписчиков.")
    try:
        async with get_async_session() as session:
            subscriber_count = await get_subscriber_stats("all", session)
        await callback_query.message.answer(f"Общее количество подписчиков: {subscriber_count}")
        await callback_query.answer()
        print(f"Общее количество подписчиков: {subscriber_count}")
    except Exception as e:
        print(f"Ошибка при получении общего количества подписчиков: {e}")


@router.callback_query(lambda c: c.data == "daily_growth")
async def daily_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за день."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за день.")
    try:
        async with get_async_session() as session:
            today_count = await get_subscriber_stats("today", session)
        await callback_query.message.answer(f"Подписки за сегодня: {today_count}")
        await callback_query.answer()
        print(f"Количество подписок за день: {today_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за день: {e}")


@router.callback_query(lambda c: c.data == "monthly_growth")
async def monthly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за месяц."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за месяц.")
    try:
        async with get_async_session() as session:
            monthly_count = await get_subscriber_stats("month", session)
        await callback_query.message.answer(f"Подписки за последний месяц: {monthly_count}")
        await callback_query.answer()
        print(f"Количество подписок за месяц: {monthly_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за месяц: {e}")


@router.callback_query(lambda c: c.data == "weekly_growth")
async def weekly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за неделю."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за неделю.")
    try:
        async with get_async_session() as session:
            weekly_count = await get_subscriber_stats("week", session)
        await callback_query.message.answer(f"Подписки за последнюю неделю: {weekly_count}")
        await callback_query.answer()
        print(f"Количество подписок за неделю: {weekly_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за неделю: {e}")


@router.callback_query(lambda c: c.data == "quarterly_growth")
async def quarterly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за квартал."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за квартал.")
    try:
        async with get_async_session() as session:
            quarterly_count = await get_subscriber_stats("quarter", session)
        await callback_query.message.answer(f"Подписки за последний квартал: {quarterly_count}")
        await callback_query.answer()
        print(f"Количество подписок за квартал: {quarterly_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за квартал: {e}")


@router.callback_query(lambda c: c.data == "half_year_growth")
async def half_year_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за полгода."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за полгода.")
    try:
        async with get_async_session() as session:
            half_year_count = await get_subscriber_stats("half_year", session)
        await callback_query.message.answer(f"Подписки за последние полгода: {half_year_count}")
        await callback_query.answer()
        print(f"Количество подписок за полгода: {half_year_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за полгода: {e}")


@router.callback_query(lambda c: c.data == "yearly_growth")
async def yearly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за год."""
    print(f"Обработчик вызван: {callback_query.data}")
    print("Запрос количества подписок за год.")
    try:
        async with get_async_session() as session:
            yearly_count = await get_subscriber_stats("year", session)
        await callback_query.message.answer(f"Подписки за последний год: {yearly_count}")
        await callback_query.answer()
        print(f"Количество подписок за год: {yearly_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за год: {e}")


@router.callback_query(lambda c: c.data == "broadcast_start")
async def start_broadcast(callback_query: CallbackQuery):
    """Запуск процесса рассылки через broadcast.py."""
    try:
        await callback_query.message.answer("Отправьте текст или документ (txt, doc, pdf, epub, fb2) для рассылки.")
        await callback_query.answer()
        print("Процесс рассылки инициирован.")
    except Exception as e:
        print(f"Ошибка при запуске рассылки: {e}")
