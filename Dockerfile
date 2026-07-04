# Базовый образ - официальный Python
FROM python:3.13-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Порт который слушает Django
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]