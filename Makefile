.PHONY: help up-staging down-staging logs-staging \
        up-prod down-prod logs-prod build

help:
	@echo "Available commands:"
	@echo "  make up-staging     Start staging environment"
	@echo "  make down-staging   Stop staging environment"
	@echo "  make logs-staging   Tail staging bot logs"
	@echo "  make up-prod        Start production environment"
	@echo "  make down-prod      Stop production environment"
	@echo "  make logs-prod      Tail production bot logs"
	@echo "  make build          Build docker images"

build:
	docker compose build

# -------- STAGING --------
up-staging:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

down-staging:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml down

logs-staging:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f bot

# -------- PRODUCTION --------
up-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

down-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f bot
