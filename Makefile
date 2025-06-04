# Makefile для URL Shortener Service

.PHONY: up down build rebuild logs

# Основные команды
up:
	@echo "Запуск сервисов в фоновом режиме..."
	docker-compose up -d --build
	@echo "\nПриложение доступно по адресу: http://localhost:8000"
	@echo "Документация Swagger: http://localhost:8000/docs\n"

down:
	@echo "Остановка сервисов..."
	docker-compose down

build:
	@echo "Сборка образов..."
	docker-compose build

rebuild: down build up

# Управление логами
logs:
	@echo "Просмотр логов..."
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f db

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make up       - Запуск сервисов (docker-compose up -d --build)"
	@echo "  make down     - Остановка сервисов (docker-compose down)"
	@echo "  make build    - Сборка образов"
	@echo "  make rebuild  - Пересборка и запуск"
	@echo "  make logs     - Просмотр логов всех сервисов"
	@echo "  make logs-app - Просмотр логов приложения"
	@echo "  make logs-db  - Просмотр логов БД"
	@echo "  make help     - Показать эту справку"
