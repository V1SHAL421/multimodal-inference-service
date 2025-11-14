# Multi-stage build for worker
FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY worker/requirements.txt requirements-worker.txt
RUN pip install --user --no-cache-dir -r requirements.txt -r requirements-worker.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY src/ ./src/
COPY worker/ ./worker/

RUN mkdir -p /app/models

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
