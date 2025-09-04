.PHONY: docker-build docker-up docker-down docker-migrate docker-superuser docker-shell docker-logs docker-clean

help:
	@echo "Docker Development:"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start all services (Django + PostgreSQL + Redis)"
	@echo "  make docker-migrate   - Run database migrations in container"
	@echo "  make docker-superuser - Create Django superuser in container"
	@echo "  make docker-down      - Stop all services"
	@echo "  make docker-shell     - Open shell in Django container"
	@echo "  make docker-logs      - View logs from all services"
	@echo "  make docker-clean     - Remove all Docker containers and volumes"

# Docker commands
build:
	docker-compose build

start:
	@echo "Starting Docker services..."
	@echo "Using .env.docker for configuration"
	docker-compose up -d
	@echo "Services starting up..."
	@echo "Django: http://localhost:8000"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo ""
	@echo "To view logs: make docker-logs"
	@echo "To access shell: make docker-shell"

stop:
	docker-compose down

restart:
	$(MAKE) stop
	$(MAKE) start

shell:
	docker-compose exec web bash

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	@echo "Creating superuser with username: $(shell whoami)"
	docker-compose exec -e DJANGO_SUPERUSER_USERNAME=$(shell whoami) \
		-e DJANGO_SUPERUSER_EMAIL="" \
		-e DJANGO_SUPERUSER_PASSWORD=admin \
		web python manage.py createsuperuser --noinput || echo "User may already exist"

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f