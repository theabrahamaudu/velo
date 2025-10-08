# Load environment variables
include .env
export $(shell sed 's/=.*//' .env)

# Paths
DB_DIR=velo/db
ALEMBIC=cd $(DB_DIR) && alembic

# Database container name (update if needed)
DB_CONTAINER=velo-postgres

.PHONY: up down logs migrate upgrade downgrade dbshell rebuild

# 🐘 Start Docker services (DB + pgAdmin + others)
up:
	docker compose up -d

# 🧹 Stop containers
down:
	docker compose down

# 📜 Show container logs
logs:
	docker compose logs -f

# 🏗️ Create a new migration (example: make migrate msg="add user table")
migrate:
	$(ALEMBIC) revision --autogenerate -m "$(msg)"
	$(ALEMBIC) upgrade head

# 🚀 Apply all migrations
upgrade:
	$(ALEMBIC) upgrade head

# ⬇️ Roll back one migration
downgrade:
	$(ALEMBIC) downgrade -1

# 🧪 Open Postgres shell inside the container
dbshell:
	docker exec -it $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

# 🧱 Full rebuild: tear down + rebuild + apply migrations
rebuild:
	docker compose down -v
	docker compose up -d
	sleep 5
	make upgrade
