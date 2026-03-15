#!/usr/bin/env python3
"""Скрипт для восстановления базы данных из бэкапа."""
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


def get_latest_backup():
    """Получить последний бэкап из папки."""
    backup_dir = Path("backups")
    if not backup_dir.exists():
        print("❌ Папка backups не найдена")
        return None
    
    backups = sorted(backup_dir.glob("backup_*.sql"), reverse=True)
    if not backups:
        print("❌ Бэкапы не найдены")
        return None
    
    return backups[0]


def restore_backup(backup_file: Path):
    """Восстановить базу данных из бэкапа."""
    if not backup_file.exists():
        print(f"❌ Файл бэкапа не найден: {backup_file}")
        return False
    
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
        print(f"♻️  Восстановление из {backup_file}...")
        print("⚠️  Все текущие данные будут удалены!")
        
        # Сначала удаляем все таблицы
        drop_cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", dbname,
            "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        ]
        
        subprocess.run(drop_cmd, env=env, capture_output=True, check=True)
        print("🗑️  Старые данные удалены")
        
        # Восстанавливаем из бэкапа
        restore_cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", username,
            "-d", dbname,
            "-f", str(backup_file)
        ]
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ База данных успешно восстановлена из {backup_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка восстановления: {e.stderr}")
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
    if len(sys.argv) > 1:
        # Восстановление из указанного файла
        backup_file = Path(sys.argv[1])
    else:
        # Восстановление из последнего бэкапа
        backup_file = get_latest_backup()
        if not backup_file:
            print("❌ Бэкапы не найдены")
            sys.exit(1)
        print(f"📦 Используется последний бэкап: {backup_file}")
    
    # Подтверждение
    response = input(f"\n⚠️  Восстановить БД из {backup_file.name}? Все текущие данные будут удалены! (yes/no): ")
    if response.lower() != "yes":
        print("❌ Отменено")
        sys.exit(0)
    
    if restore_backup(backup_file):
        print(f"\n✅ База данных восстановлена из {backup_file}")
    else:
        print("\n❌ Не удалось восстановить базу данных")
        sys.exit(1)

