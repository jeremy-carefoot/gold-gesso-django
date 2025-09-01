.PHONY: help venv install migrate superuser run test clean docker-build docker-up docker-down docker-migrate docker-superuser docker-shell docker-logs docker-clean

help:
	@echo "Available commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make venv        - Create virtual environment and install dependencies"
	@echo "  make install     - Install/update dependencies from requirements.txt"
	@echo "  make migrate     - Run Django database migrations"
	@echo "  make superuser   - Create Django superuser"
	@echo "  make run         - Start Django development server"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove virtual environment and cache files"
	@echo ""
	@echo "Docker Development:"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start all services (Django + PostgreSQL + Redis)"
	@echo "  make docker-migrate   - Run database migrations in container"
	@echo "  make docker-superuser - Create Django superuser in container"
	@echo "  make docker-down      - Stop all services"
	@echo "  make docker-shell     - Open shell in Django container"
	@echo "  make docker-logs      - View logs from all services"
	@echo "  make docker-clean     - Remove all Docker containers and volumes"

venv:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "Virtual environment created and dependencies installed!"
	@echo "Activate it with: source venv/bin/activate"

install:
	./venv/bin/pip install -r requirements.txt

migrate:
	./venv/bin/python manage.py makemigrations
	./venv/bin/python manage.py migrate

superuser:
	@echo "Creating superuser with username: $(shell whoami)"
	DJANGO_SUPERUSER_USERNAME=$(shell whoami) \
	DJANGO_SUPERUSER_EMAIL="" \
	DJANGO_SUPERUSER_PASSWORD=admin \
	./venv/bin/python manage.py createsuperuser --noinput || echo "User may already exist"

run:
	./venv/bin/python manage.py runserver

test:
	./venv/bin/python manage.py test

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f db.sqlite3

# Docker commands
docker-build:
	docker-compose build

docker-up:
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

docker-down:
	docker-compose down

docker-shell:
	docker-compose exec web bash

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-superuser:
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