.PHONY: help install run test clean docker-up docker-down migrate

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
