FROM python:3.13-slim

WORKDIR /app

# Установка минимальных build зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Удаление build зависимостей для уменьшения размера
RUN apt-get purge -y --auto-remove build-essential

# Копирование кода приложения
COPY . .

# Создание папки для логов
RUN mkdir -p logs

# Порт приложения
EXPOSE 8000

# Запуск приложения
CMD ["python", "main.py"]
