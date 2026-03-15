# Система бэкапов базы данных

## Описание

Система автоматического создания и восстановления бэкапов PostgreSQL базы данных.

## Требования

- PostgreSQL клиент (`pg_dump` и `psql` должны быть установлены)
- Доступ к базе данных (настройки в `.env`)

## Команды

### 1. Создать бэкап

```bash
make backup
```

или

```bash
python scripts/backup_db.py
```

Создает файл бэкапа в папке `backups/` с именем `backup_YYYYMMDD_HHMMSS.sql`

### 2. Восстановить из последнего бэкапа

```bash
make restore
```

или

```bash
python scripts/restore_db.py
```

Автоматически находит последний бэкап и восстанавливает БД.

⚠️ **ВНИМАНИЕ**: Все текущие данные будут удалены!

### 3. Восстановить из конкретного бэкапа

```bash
python scripts/restore_db.py backups/backup_20260315_120000.sql
```

### 4. Показать список бэкапов

```bash
make list-backups
```

или

```bash
python scripts/list_backups.py
```

## Структура папки backups

```
backups/
├── backup_20260315_120000.sql  # Самый новый (🆕)
├── backup_20260314_180000.sql
└── backup_20260313_090000.sql
```

## Автоматизация

### Создание бэкапа перед важными операциями

```bash
# Перед обновлением
make backup
make migrate

# Перед восстановлением
make backup
make restore
```

### Cron задача (ежедневный бэкап в 3:00)

```bash
crontab -e
```

Добавить:
```
0 3 * * * cd /path/to/project && make backup
```

## Примеры использования

### Быстрый бэкап перед тестированием

```bash
make backup
# ... тестирование ...
make restore  # если что-то пошло не так
```

### Миграция данных

```bash
# На старом сервере
make backup

# Скопировать файл на новый сервер
scp backups/backup_*.sql user@newserver:/path/to/project/backups/

# На новом сервере
make restore
```

## Устранение неполадок

### Ошибка: pg_dump not found

Установите PostgreSQL клиент:

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-client
```

**macOS:**
```bash
brew install postgresql
```

### Ошибка: Permission denied

Проверьте права доступа к папке backups:
```bash
chmod +x scripts/backup_db.py
chmod +x scripts/restore_db.py
```

### Ошибка подключения к БД

Проверьте настройки в `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
```
