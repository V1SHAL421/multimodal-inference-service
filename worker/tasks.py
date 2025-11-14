import os
import time
import asyncio
from datetime import datetime
from typing import List, Optional, Any
import asyncpg
from worker.celery_app import celery_app
from src.utils import TextPredictor

async def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://mluser:mlpassword@localhost:5432/predictions')
    return await asyncpg.connect(database_url)

async def log_batch_prediction(inputs: List[str], predictions: List[Any], latency: float):
    """Log batch predictions to database"""
    conn = await get_db_connection()
    try:
        for input_text, prediction in zip(inputs, predictions):
            await conn.execute(
                """
                INSERT INTO predictions (modality, input_data, prediction, latency, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                'text_batch', input_text[:500], str(prediction), latency, datetime.utcnow()
            )
    finally:
        await conn.close()

@celery_app.task(bind=True, name='worker.tasks.predict_batch_task')
def predict_batch_task(self, inputs: List[str], options: Optional[dict[str, Any]] = None):
    """
    Async batch inference task
    Processes multiple inputs efficiently in batches
    """
    start_time = time.time()
    
    try:
        # Update task state
        self.update_state(state='PROCESSING', meta={'progress': 0, 'total': len(inputs)})
        
        text_predictor = TextPredictor()
        predictions = []
        
        # Process in batches for efficiency
        batch_size = 8
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            
            for input_text in batch:
                pred = text_predictor.predict(input_text)
                predictions.append(pred)
            
            # Update progress
            progress = min(i + batch_size, len(inputs))
            self.update_state(
                state='PROCESSING',
                meta={'progress': progress, 'total': len(inputs)}
            )
        
        latency = time.time() - start_time
        
        # Log to database
        asyncio.run(log_batch_prediction(inputs, predictions, latency))
        
        return {
            'predictions': predictions,
            'count': len(predictions),
            'latency': latency,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
