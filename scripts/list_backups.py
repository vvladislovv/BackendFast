#!/usr/bin/env python3
"""Скрипт для просмотра списка бэкапов."""
from pathlib import Path
from datetime import datetime


def list_backups():
    """Показать список всех бэкапов."""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        print("📭 Папка backups не найдена")
        return
    
    backups = sorted(backup_dir.glob("backup_*.sql"), reverse=True)
    
    if not backups:
        print("📭 Бэкапы не найдены")
        return
    
    print(f"\n📋 Найдено бэкапов: {len(backups)}\n")
    
    for i, backup in enumerate(backups, 1):
        size_kb = backup.stat().st_size / 1024
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        
        # Парсим дату из имени файла
        try:
            date_str = backup.stem.replace("backup_", "")
            backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            date_formatted = backup_date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date_formatted = mtime.strftime("%Y-%m-%d %H:%M:%S")
        
        marker = "🆕" if i == 1 else "  "
        print(f"{marker} {i}. {backup.name}")
        print(f"     Дата: {date_formatted}")
        print(f"     Размер: {size_kb:.2f} KB")
        print()


if __name__ == "__main__":
    list_backups()
