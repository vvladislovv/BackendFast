#!/usr/bin/env python3
"""Проверка окружения перед запуском."""
import sys
import subprocess


def check_python_version():
    """Проверка версии Python."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor != 13:
        print("⚠️  Рекомендуется Python 3.13 (у вас {}.{})".format(
            version.major, version.minor
        ))
        return False
    return True


def check_dependencies():
    """Проверка установленных зависимостей."""
    try:
        import litestar
        print(f"✓ Litestar {litestar.__version__}")
    except ImportError:
        print("✗ Litestar не установлен")
        return False
    
    try:
        import sqlalchemy
        print(f"✓ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        print("✗ SQLAlchemy не установлен")
        return False
    
    try:
        import pydantic
        print(f"✓ Pydantic {pydantic.__version__}")
    except ImportError:
        print("✗ Pydantic не установлен")
        return False
    
    return True


def check_env_file():
    """Проверка наличия .env файла."""
    import os
    if os.path.exists('.env'):
        print("✓ .env файл найден")
        return True
    else:
        print("✗ .env файл не найден")
        print("  Создайте его: cp .env.example .env")
        return False


def check_postgres():
    """Проверка доступности PostgreSQL."""
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ PostgreSQL установлен")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  PostgreSQL не найден (опционально для локальной разработки)")
    return True


def main():
    """Главная функция проверки."""
    print("Проверка окружения...\n")
    
    checks = [
        ("Python версия", check_python_version()),
        ("Зависимости", check_dependencies()),
        (".env файл", check_env_file()),
        ("PostgreSQL", check_postgres()),
    ]
    
    print("\n" + "="*50)
    all_passed = all(result for _, result in checks)
    
    if all_passed:
        print("✓ Все проверки пройдены!")
        print("\nМожно запускать:")
        print("  python main.py")
    else:
        print("⚠️  Некоторые проверки не пройдены")
        print("\nУстановите зависимости:")
        print("  pip install -r requirements.txt")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
