from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_client_type_keyboard():
    """Клавиатура для выбора типа клиента."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я организатор мероприятий", callback_data="client_type:organizer")],
        [InlineKeyboardButton(text="Я индивидуальный клиент", callback_data="client_type:individual")]
    ])
    return keyboard


def get_main_menu_keyboard(is_organizer=False):
    """Основное меню для всех клиентов, с дополнительными кнопками для организаторов."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать погоду в Сочи", callback_data="weather")],
        [InlineKeyboardButton(text="Наши соцсети", callback_data="social_networks")],
        [InlineKeyboardButton(text="Анонсы мероприятий", callback_data="announcements")],
        [InlineKeyboardButton(text="Мы на картах", callback_data="maps")],
        [InlineKeyboardButton(text="Контактные данные", callback_data="contact_details")],
        [InlineKeyboardButton(text="Наш сайт", callback_data="website")],
        [InlineKeyboardButton(text="Интернет магазин", callback_data="store")],
        [InlineKeyboardButton(text="Видео", callback_data="video")],
        [InlineKeyboardButton(text="Правила проживания", callback_data="rules")],
        [InlineKeyboardButton(text="Как добраться", callback_data="directions")]
    ])

    # Добавляем дополнительные кнопки для организаторов
    if is_organizer:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Предложение для организаторов", callback_data="organizer_guide")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Чат для организаторов", callback_data="organizer_chat")])

    return keyboard