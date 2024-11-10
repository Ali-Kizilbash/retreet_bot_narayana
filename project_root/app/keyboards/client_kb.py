from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_client_type_keyboard():
    """Клавиатура для выбора типа клиента."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я организатор мероприятий", callback_data="client_type:organizer")],
        [InlineKeyboardButton(text="Я индивидуальный клиент", callback_data="client_type:individual")]
    ])
    return keyboard


def get_organizer_combined_menu_keyboard():
    """Клавиатура для организатора мероприятий с объединёнными кнопками."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Предложение для организаторов", callback_data="organizer_guide")],
        [InlineKeyboardButton(text="Правила проживания", callback_data="rules")],
        [InlineKeyboardButton(text="Как добраться", callback_data="directions")]
    ])
    return keyboard


def get_general_menu_keyboard():
    """Общая клавиатура для всех клиентов с кнопками для получения информации."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Правила проживания", callback_data="rules")],
        [InlineKeyboardButton(text="Как добраться", callback_data="directions")]
    ])
    return keyboard
