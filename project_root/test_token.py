import requests

# Подставьте ваш токен сюда
token = "7644663625:AAG8fRwdoJNY3od8y0lPtx2soUmBToKZ6oA"
url = f"https://api.telegram.org/bot{token}/getMe"

try:
    response = requests.get(url)
    if response.status_code == 200:
        print("Бот авторизован! Информация о боте:", response.json())
    else:
        print("Ошибка авторизации:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print("Ошибка при подключении к Telegram API:", e)