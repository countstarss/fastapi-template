# fastapi_template/worker.py
import os
from celery import Celery

from fastapi_template.core.config import settings

# MARK: 创建Celery应用
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["fastapi_template.tasks"]
)

# MARK: 可选：配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)