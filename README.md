# RT Camera Monitor

Web-портал мониторинга камер Ростелеком.

## Запуск

```bash
# Активировать виртуальное окружение
source .venv/bin/activate

# Установить зависимости
uv pip install -r requirements.txt

# Запустить
python app.py
```

Портал доступен по адресу: http://localhost:5000

## Конфигурация

API-ключ задаётся в файле `.env`:

```
API_KEY=your_api_key_here
```
