.PHONY: help build up down restart logs migrate init test clean

help:
	@echo "DWC Shop Backend - Команды управления"
	@echo ""
	@echo "  make build     - Собрать Docker образы"
	@echo "  make up        - Запустить сервисы"
	@echo "  make down      - Остановить сервисы"
	@echo "  make restart   - Перезапустить сервисы"
	@echo "  make logs      - Показать логи"
	@echo "  make migrate   - Создать новую миграцию"
	@echo "  make init      - Инициализировать базу данных"
	@echo "  make test      - Запустить тесты"
	@echo "  make clean     - Очистить volumes и контейнеры"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Сервисы запущены"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f backend

migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

init:
	docker-compose exec backend python -m app.init_db

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	docker system prune -f
