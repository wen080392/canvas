.PHONY: up install backend-install frontend-install

up:
	docker-compose up -d

install: backend-install frontend-install

backend-install:
	cd apps/backend && poetry install

frontend-install:
	cd apps/frontend && npm install
