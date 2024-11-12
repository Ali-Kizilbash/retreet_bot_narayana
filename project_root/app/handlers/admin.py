from aiogram import Router, types  #admin.py
from aiogram.types import CallbackQuery, InputFile
from aiogram.filters import Command
import os
from app.keyboards.admin_kb import (get_admin_menu, get_file_management_menu,
                                    get_subscriber_stats_menu)
from app.database.crud import get_subscriber_stats  # Функция для получения статистики

router = Router()

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

# Здесь можно добавить обработчики для добавления, редактирования и удаления файлов

@router.callback_query(lambda c: c.data == "subscriber_stats")
async def subscriber_stats(callback_query: CallbackQuery):
    """Показывает меню для просмотра статистики подписчиков."""
    print("Вызвано меню статистики подписчиков.")
    try:
        await callback_query.message.answer("Статистика подписчиков:", reply_markup=get_subscriber_stats_menu())
        await callback_query.answer()
        print("Меню статистики подписчиков успешно отображено.")
    except Exception as e:
        print(f"Ошибка при отображении меню статистики подписчиков: {e}")

@router.callback_query(lambda c: c.data == "current_subscribers")
async def current_subscribers(callback_query: CallbackQuery):
    """Показывает текущее количество подписчиков."""
    print("Запрос текущего количества подписчиков.")
    try:
        subscriber_count = await get_subscriber_stats("current")
        await callback_query.message.answer(f"Текущее количество подписчиков: {subscriber_count}")
        await callback_query.answer()
        print(f"Текущее количество подписчиков: {subscriber_count}")
    except Exception as e:
        print(f"Ошибка при получении текущего количества подписчиков: {e}")

@router.callback_query(lambda c: c.data == "daily_growth")
async def daily_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за день."""
    print("Запрос количества подписок за день.")
    try:
        today_count = await get_subscriber_stats("daily")
        await callback_query.message.answer(f"Подписки за сегодня: {today_count}")
        await callback_query.answer()
        print(f"Количество подписок за день: {today_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за день: {e}")

@router.callback_query(lambda c: c.data == "monthly_growth")
async def monthly_growth(callback_query: CallbackQuery):
    """Показывает количество подписок за месяц."""
    print("Запрос количества подписок за месяц.")
    try:
        monthly_count = await get_subscriber_stats("monthly")
        await callback_query.message.answer(f"Подписки за последний месяц: {monthly_count}")
        await callback_query.answer()
        print(f"Количество подписок за последний месяц: {monthly_count}")
    except Exception as e:
        print(f"Ошибка при получении количества подписок за месяц: {e}")

@router.callback_query(lambda c: c.data == "custom_range")
async def custom_range(callback_query: CallbackQuery):
    """Запрос временного диапазона для статистики подписчиков."""
    print("Запрос пользовательского диапазона для статистики подписчиков.")
    try:
        await callback_query.message.answer("Функционал выбора пользовательского диапазона пока в разработке.")
        await callback_query.answer()
        print("Уведомление о разработке функции пользовательского диапазона отправлено.")
    except Exception as e:
        print(f"Ошибка при обработке пользовательского диапазона: {e}")
