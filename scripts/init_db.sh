#!/bin/bash

echo "Инициализация базы данных..."

# Создание первой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

echo "База данных инициализирована!"
