# fastapi_template/tasks/__init__.py
from fastapi_template.worker import celery_app

@celery_app.task
def example_task(word: str) -> str:
    return f"Task completed: {word}"

@celery_app.task
def send_email_task(
    to: str,
    subject: str,
    body: str,
    html: str = None
) -> bool:
    from fastapi_template.lib.email import email_service
    return email_service.send_email(
        to=to,
        subject=subject,
        body=body,
        html=html
    )