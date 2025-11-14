.PHONY: build up down logs clean test scale-api scale-worker

# Build all containers
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start with logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean everything (including volumes)
clean:
	docker-compose down -v
	docker system prune -f

# Scale API instances
scale-api:
	docker-compose up -d --scale api=3

# Scale workers
scale-worker:
	docker-compose up -d --scale worker=4

# Test API
test:
	curl http://localhost/health
	@echo "\n"
	curl -X POST http://localhost/predict/text \
		-H "Content-Type: application/json" \
		-d '{"input_text": "test prediction"}'

# View metrics
metrics:
	curl http://localhost/metrics

# Restart specific service
restart-api:
	docker-compose restart api

restart-worker:
	docker-compose restart worker
