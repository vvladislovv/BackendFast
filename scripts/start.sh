#!/bin/bash

echo "Запуск Backend API..."

# Активация виртуального окружения (если есть)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск сервера
python main.py
