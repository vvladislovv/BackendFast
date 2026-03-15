.PHONY: help install run test clean docker-up docker-down migrate backup restore list-backups clear-db

help:
	@echo "Доступные команды:"
	@echo "  make install      - Установить зависимости"
	@echo "  make run          - Запустить API сервер"
	@echo "  make bot          - Запустить Telegram бота"
	@echo "  make test         - Запустить тесты"
	@echo "  make migrate      - Применить миграции"
	@echo "  make migration    - Создать новую миграцию"
	@echo "  make docker-up    - Запустить через Docker (полный стек)"
	@echo "  make docker-dev   - Запустить только БД для разработки"
	@echo "  make docker-down  - Остановить Docker контейнеры"
	@echo "  make backup       - Создать бэкап базы данных"
	@echo "  make restore      - Восстановить БД из последнего бэкапа"
	@echo "  make list-backups - Показать список всех бэкапов"
	@echo "  make clear-db     - Очистить базу данных (удалить все данные)"
	@echo "  make clean        - Очистить временные файлы"
	@echo "  make logs         - Показать логи"

install:
	pip install -r requirements.txt

run:
	python main.py

bot:
	python integrations/telegram/bot.py

test:
	pytest -v

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

docker-up:
	docker-compose up -d

docker-dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "PostgreSQL запущен на localhost:5432"
	@echo "Теперь запустите API локально: python main.py"

docker-down:
	docker-compose down

docker-dev-down:
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build --no-cache

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

logs:
	tail -f logs/app_*.json

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

backup:
	@echo "📦 Создание бэкапа базы данных..."
	@export PATH="/opt/homebrew/opt/postgresql@16/bin:$$PATH" && python3 scripts/backup_db.py

restore:
	@echo "♻️  Восстановление базы данных из последнего бэкапа..."
	@export PATH="/opt/homebrew/opt/postgresql@16/bin:$$PATH" && python3 scripts/restore_db.py

list-backups:
	@python3 scripts/list_backups.py

clear-db:
	@echo "🗑️  Очистка базы данных..."
	@export PATH="/opt/homebrew/opt/postgresql@16/bin:$$PATH" && python3 scripts/clear_db.py
