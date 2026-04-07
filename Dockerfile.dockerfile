FROM python:3.10-slim

WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (если нужно)
RUN python manage.py collectstatic --noinput

# Запускаем gunicorn
CMD ["gunicorn", "irina_realty.wsgi:application", "--bind", "0.0.0.0:8000"]
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "irina_reality.wsgi:application"]