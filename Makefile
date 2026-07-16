.PHONY: install dev start backend frontend build test lint

install:
	python3 -m venv .venv
	.venv/bin/pip install -e '.[dev]'
	cd web && npm install

dev:
	@echo "Backend: make backend"
	@echo "Frontend: make frontend"

start:
	.venv/bin/python scripts/start.py

backend:
	.venv/bin/uvicorn app.main:app --reload --port 8787 --env-file .env

frontend:
	cd web && npm run dev

build:
	cd web && npm run build

test:
	.venv/bin/pytest
	cd web && npm run test

lint:
	.venv/bin/ruff check app tests
	cd web && npm run lint

