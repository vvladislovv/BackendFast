#!/usr/bin/env python3
"""Скрипт для создания бэкапа базы данных."""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def load_env():
    """Загрузить переменные из .env файла."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Файл .env не найден")
        sys.exit(1)
    
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def create_backup():
    """Создать бэкап базы данных."""
    # Загружаем переменные окружения
    env_vars = load_env()
    database_url = env_vars.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не найден в .env")
        return None
    
    # Создаем папку для бэкапов
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Генерируем имя файла с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql"
    
    # Парсим DATABASE_URL
    # postgresql+asyncpg://user:password@host:port/dbname
    db_url = database_url.replace("postgresql+asyncpg://", "")
    
    if "@" in db_url:
        credentials, host_db = db_url.split("@")
        username, password = credentials.split(":")
        host_port, dbname = host_db.split("/")
        
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host = host_port
            port = "5432"
    else:
        print("❌ Неверный формат DATABASE_URL")
        return None
    
    # Устанавливаем переменную окружения для пароля
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    try:
        # Выполняем pg_dump
        print(f"📦 Создание бэкапа в {backup_file}...")
        
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", dbname,
            "-F", "p",  # plain text format
            "-f", str(backup_file)
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        size_kb = backup_file.stat().st_size / 1024
        print(f"✅ Бэкап успешно создан: {backup_file}")
        print(f"📊 Размер файла: {size_kb:.2f} KB")
        return backup_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания бэкапа: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ pg_dump не найден. Установите PostgreSQL клиент:")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql-client")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    backup_file = create_backup()
    if not backup_file:
        sys.exit(1)

