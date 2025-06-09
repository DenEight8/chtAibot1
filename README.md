# chtAibot1
Чат-бот для взаємодії з БД користувачів з інтегрованим ШІ

## Запуск проекту
1. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```
2. Застосуйте міграції:
   ```bash
   python manage.py migrate
   ```
3. Запустіть сервер розробки:
   ```bash
   python manage.py runserver
   ```

## Змінні оточення
Для роботи інтеграції з OpenAI необхідно визначити змінну `OPENAI_API_KEY` у системному оточенні або у `.env` файлі.
