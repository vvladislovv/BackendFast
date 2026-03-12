#!/usr/bin/env python3
"""Генерация SECRET_KEY для .env файла."""
import secrets


def generate_secret_key(length=32):
    """Генерация безопасного SECRET_KEY."""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    secret = generate_secret_key()
    print("Сгенерирован SECRET_KEY:")
    print(f"\nSECRET_KEY={secret}")
    print("\nДобавьте эту строку в ваш .env файл")
