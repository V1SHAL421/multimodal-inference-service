# ML Microservices with Docker

Production-ready containerized ML inference system with FastAPI, Celery workers, PostgreSQL, Nginx load balancing, and Prometheus monitoring.

## Architecture

```
┌─────────┐      ┌───────────┐      ┌─────────┐
│ Client  │─────▶│   Nginx   │─────▶│   API   │
└─────────┘      │  (Proxy)  │      │ FastAPI │
                 └───────────┘      └─────────┘
                                         │
                      ┌──────────────────┼──────────────────┐
                      ▼                  ▼                  ▼
                 ┌─────────┐       ┌─────────┐       ┌──────────┐
                 │  Redis  │       │ Worker  │       │ Postgres │
                 │ (Broker)│       │ Celery  │       │   (DB)   │
                 └─────────┘       └─────────┘       └──────────┘
                                         │
                                         ▼
                                   ┌──────────┐
                                   │Prometheus│
                                   │ Grafana  │
                                   └──────────┘
```

## Services

- **api**: FastAPI endpoint for real-time predictions
- **worker**: Celery worker for async batch inference
- **db**: PostgreSQL for storing predictions and logs
- **proxy**: Nginx for load balancing and rate limiting
- **redis**: Message broker for Celery
- **prometheus**: Metrics collection
- **grafana**: Metrics visualization (admin/admin)

## Quick Start

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f worker

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Endpoints

- **API**: http://localhost:80 (via Nginx) or http://localhost:8000 (direct)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### API Usage

```bash
# Health check
curl http://localhost/health

# Single prediction
curl -X POST http://localhost/predict/text \
  -H "Content-Type: application/json" \
  -d '{"input_text": "your text here"}'

# Batch prediction (async)
curl -X POST http://localhost/predict/text/batch \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["text1", "text2", "text3"]}'

# Check batch status
curl http://localhost/predict/status/{task_id}

# View metrics
curl http://localhost/metrics
```

## Scaling

Scale API instances:
```bash
docker-compose up -d --scale api=3
```

Scale workers:
```bash
docker-compose up -d --scale worker=4
```

Update `proxy/nginx.conf` to add more API backends for load balancing.

## Optimization Tips

1. **Multi-stage builds**: Reduces image size by ~60%
2. **Layer caching**: Dependencies installed separately from code
3. **Health checks**: Ensures services are ready before routing traffic
4. **Connection pooling**: PostgreSQL pool for efficient DB access
5. **Batch processing**: Worker processes multiple inputs efficiently
6. **Rate limiting**: Nginx prevents API abuse

## Monitoring

View metrics in Prometheus:
- `prediction_requests_total`: Total requests by modality and status
- `prediction_latency_seconds`: Latency histogram

Query examples:
```promql
# Request rate
rate(prediction_requests_total[5m])

# Average latency
rate(prediction_latency_seconds_sum[5m]) / rate(prediction_latency_seconds_count[5m])

# Error rate
rate(prediction_requests_total{status="error"}[5m])
```

## Development

Mount local code for hot reload:
```yaml
volumes:
  - ./src:/app/src  # Already configured
```

The API service uses `--reload` flag for auto-restart on code changes.

## Production Considerations

1. Use secrets management (not env vars in docker-compose)
2. Add authentication/authorization
3. Configure proper logging aggregation
4. Set up backup strategy for PostgreSQL
5. Use container orchestration (Kubernetes) for production
6. Add SSL/TLS termination at proxy
7. Implement circuit breakers and retries
8. Add model versioning and A/B testing
