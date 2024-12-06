# Используем официальный образ Python в качестве базового
FROM python:3.13-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения в контейнер
COPY . .

# Определяем команду для запуска бота
CMD ["python", "bot.py"]
