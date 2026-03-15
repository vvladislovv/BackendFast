#!/usr/bin/env python3
"""Скрипт для полной очистки базы данных."""
import os
import sys
import subprocess
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


def clear_database():
    """Очистить все таблицы в базе данных."""
    # Загружаем переменные окружения
    env_vars = load_env()
    database_url = env_vars.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не найден в .env")
        return False
    
    # Парсим DATABASE_URL
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
        return False
    
    # Устанавливаем переменную окружения для пароля
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    try:
        print("🗑️  Очистка базы данных...")
        
        # SQL команда для очистки всех таблиц
        sql_command = """
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' RESTART IDENTITY CASCADE';
            END LOOP;
        END $$;
        """
        
        cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", dbname,
            "-c", sql_command
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ База данных полностью очищена!")
        print("📊 Все таблицы пусты (кроме alembic_version)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка очистки: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ psql не найден. Установите PostgreSQL клиент:")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql-client")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    print("⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные из базы данных!")
    response = input("Продолжить? (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Отменено")
        sys.exit(0)
    
    if clear_database():
        print("\n✅ База данных очищена. Можно начинать тестирование с чистого листа!")
    else:
        print("\n❌ Не удалось очистить базу данных")
        sys.exit(1)

