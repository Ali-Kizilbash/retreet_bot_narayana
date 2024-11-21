import os
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Пути к файлу с сотрудниками и владельцу
STAFF_USERNAMES_FILE = "staff_usernames.txt"
OWNER_USERNAME = "@Veniamin_tk"

# Список ID сотрудников
STAFF_IDS = [502332805, 309106647, 1975738954, 1347328315, 6807438126]

def is_staff(user_id: int = None, username: str = None) -> bool:
    """
    Проверяет, является ли пользователь сотрудником (администратором).
    Можно проверять как по user_id, так и по username.

    :param user_id: ID пользователя (целое число)
    :param username: Имя пользователя (строка, включая @)
    :return: True, если пользователь сотрудник, иначе False
    """
    # Проверка по user_id
    if user_id is not None:
        if user_id in STAFF_IDS:
            return True

    # Проверка по username
    if username is not None:
        # Если файла с именами сотрудников нет, предупреждаем в логах
        if not os.path.exists(STAFF_USERNAMES_FILE):
            logger.warning(f"Файл {STAFF_USERNAMES_FILE} не найден.")
            return username == OWNER_USERNAME  # Владельцу доступ разрешён всегда

        try:
            with open(STAFF_USERNAMES_FILE, "r") as f:
                staff_usernames = f.read().splitlines()
            return username in staff_usernames or username == OWNER_USERNAME
        except Exception as e:
            logger.error(f"Ошибка при проверке файла сотрудников: {e}")
            return False

    # Если ни user_id, ни username не указаны, возвращаем False
    return False
