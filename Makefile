.PHONY: help venv install migrate run test clean

help:
	@echo "Available commands:"
	@echo "  make venv        - Create virtual environment and install dependencies"
	@echo "  make install     - Install/update dependencies from requirements.txt"
	@echo "  make migrate     - Run Django database migrations"
	@echo "  make run         - Start Django development server"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove virtual environment and cache files"

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

run:
	./venv/bin/python manage.py runserver

test:
	./venv/bin/python manage.py test

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f db.sqlite3