#!/usr/bin/env python3
"""Скрипт для создания администратора (пример)."""
import asyncio
from core.security import get_password_hash


async def create_admin():
    """Создание администратора."""
    print("Создание администратора")
    print("="*50)
    
    username = input("Имя пользователя: ")
    password = input("Пароль: ")
    
    hashed_password = get_password_hash(password)
    
    print("\nДанные администратора:")
    print(f"Username: {username}")
    print(f"Hashed password: {hashed_password}")
    print("\nСохраните эти данные в базе данных")


if __name__ == "__main__":
    asyncio.run(create_admin())
