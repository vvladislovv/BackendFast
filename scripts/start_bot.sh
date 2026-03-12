#!/bin/bash

echo "Запуск Telegram бота..."

# Активация виртуального окружения (если есть)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск бота
python integrations/telegram/bot.py
