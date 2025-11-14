import os
import time
from typing import Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import asyncpg
from contextlib import asynccontextmanager

from src.utils import TextPredictor
from worker.tasks import predict_batch_task

# Prometheus metrics
REQUEST_COUNT = Counter('prediction_requests_total', 'Total prediction requests', ['modality', 'status'])
REQUEST_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency', ['modality'])

# Database connection pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool
    database_url = os.getenv('DATABASE_URL', 'postgresql://mluser:mlpassword@localhost:5432/predictions')
    db_pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    yield
    # Shutdown
    await db_pool.close()

app = FastAPI(title="ML Inference API", lifespan=lifespan)

class PredictionRequest(BaseModel):
    input_text: str
    options: Optional[dict[str, Any]] = None

class BatchPredictionRequest(BaseModel):
    inputs: list[str]
    options: Optional[dict[str, Any]] = None

async def log_prediction(modality: str, input_data: str, prediction: Any, latency: float):
    """Log prediction to database"""
    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO predictions (modality, input_data, prediction, latency, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                modality, input_data[:500], str(prediction), latency, datetime.utcnow()
            )

@app.get("/")
def read_root():
    return {"service": "ML Inference API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict/text")
async def predict_text(request: PredictionRequest, background_tasks: BackgroundTasks):
    """Synchronous text prediction"""
    start_time = time.time()
    
    try:
        text_predictor = TextPredictor()
        inputs = {"input_text": request.input_text}
        
        if not text_predictor.validate_inputs(inputs, request.options):
            REQUEST_COUNT.labels(modality='text', status='error').inc()
            raise HTTPException(status_code=400, detail="Invalid inputs")
        
        result = text_predictor.predict(request.input_text)
        latency = time.time() - start_time
        
        # Log to database in background
        background_tasks.add_task(log_prediction, 'text', request.input_text, result, latency)
        
        REQUEST_COUNT.labels(modality='text', status='success').inc()
        REQUEST_LATENCY.labels(modality='text').observe(latency)
        
        return {
            "prediction": result,
            "latency": latency,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        REQUEST_COUNT.labels(modality='text', status='error').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/text/batch")
async def predict_text_batch(request: BatchPredictionRequest):
    """Async batch prediction using Celery worker"""
    try:
        # Send to Celery worker for async processing
        task = predict_batch_task.delay(request.inputs, request.options)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Batch prediction submitted to worker queue"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/status/{task_id}")
async def get_task_status(task_id: str):
    """Check status of async batch prediction"""
    from worker.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.ready():
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task.result
        }
    else:
        return {
            "task_id": task_id,
            "status": "processing"
        }
