#!/usr/bin/env python3
"""Простой тест статических файлов"""
import requests

# Тестируем доступ к статическим файлам
try:
    response = requests.get("http://localhost:8000/uploads/photos/test.txt", timeout=5)
    print(f"Статус: {response.status_code}")
    print(f"Содержимое: {response.text}")
except Exception as e:
    print(f"Ошибка: {e}")