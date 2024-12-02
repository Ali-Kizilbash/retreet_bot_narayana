from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_menu():
    """Клавиатура для админ-панели."""
    try:
        print("Создание клавиатуры админ-панели.")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Управление файлами", callback_data="manage_files")],
            [InlineKeyboardButton(text="Статистика подписчиков", callback_data="subscriber_stats")],
            [InlineKeyboardButton(text="Запустить рассылку", callback_data="broadcast_start")]  # Кнопка для рассылки
        ])
        print("Клавиатура админ-панели создана успешно.")
        return keyboard
    except Exception as e:
        print(f"Ошибка при создании клавиатуры админ-панели: {e}")


def get_file_management_menu():
    """Клавиатура для управления файлами."""
    try:
        print("Создание клавиатуры управления файлами.")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Просмотреть файлы", callback_data="view_files")],
            [InlineKeyboardButton(text="Добавить файл", callback_data="add_file")],
            [InlineKeyboardButton(text="Редактировать файл", callback_data="edit_file")],
            [InlineKeyboardButton(text="Удалить файл", callback_data="delete_file")]
        ])
        print("Клавиатура управления файлами создана успешно.")
        return keyboard
    except Exception as e:
        print(f"Ошибка при создании клавиатуры управления файлами: {e}")


def get_subscriber_stats_menu():
    """Клавиатура для статистики подписчиков."""
    try:
        print("Создание клавиатуры статистики подписчиков.")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Текущие подписчики", callback_data="current_subscribers")],
            [InlineKeyboardButton(text="Подписки за сегодня", callback_data="daily_growth")],
            [InlineKeyboardButton(text="Подписки за неделю", callback_data="weekly_growth")],
            [InlineKeyboardButton(text="Подписки за месяц", callback_data="monthly_growth")],
            [InlineKeyboardButton(text="Подписки за квартал", callback_data="quarterly_growth")],
            [InlineKeyboardButton(text="Подписки за полгода", callback_data="half_year_growth")],
            [InlineKeyboardButton(text="Подписки за год", callback_data="yearly_growth")]
        ])
        print("Клавиатура статистики подписчиков создана успешно.")
        return keyboard
    except Exception as e:
        print(f"Ошибка при создании клавиатуры статистики подписчиков: {e}")
