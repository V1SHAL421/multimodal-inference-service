from celery import Celery

app = Celery('multimodal_service', broker='redis://localhost:6379')
app.conf.update(
    # Serialize tasks using JSON
    task_serializer='json',
    accept_content=['json'],  # Accept only JSON serialized content
    result_serializer='json',  # Serialize results using JSON

    # Results
    result_expires=3600,  # 1 hour
    result_persistent=True,
    result_extended=True,

    # Routing
    task_routes={
        'tasks.predict_text_input': {'queue': 'text_queue'},
    },

    # Worker behaviour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_concurrency=4,
    worker_max_tasks_per_child=100,

    # Reliability & Broker settings
    broker_connection_retry_on_startup=True,
    broker_transport_options={'visibility_timeout': 3600},
    broker_heartbeat=10,
    broker_pool_limit=10,

    # Time limits
    task_soft_time_limit=300,
    task_time_limit=600,
    task_reject_on_worker_lost=True,

    # Metrics
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_track_started=True,
    task_publish_retry=True,
    task_default_retry_delay=60,
    task_max_retries=3,

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)