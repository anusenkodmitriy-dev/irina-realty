# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=irina_realty.settings

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (если нужно)
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Запускаем Gunicorn с правильным указанием WSGI-приложения
# Важно: irina_realty.wsgi — потому что папка называется irina_realty, а внутри неё есть wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "irina_realty.wsgi:application"]
