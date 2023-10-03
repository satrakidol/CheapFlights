from celery.schedules import crontab

REDIS_HOST = "0.0.0.0"
REDIS_PORT = 6379
BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_IMPORTS = ('project.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'project.tasks.print_hello',
        # Every minute
        'schedule': crontab(minute="*"),
    },
    'email': {
    'task':'project.tasks.email',
    'schedule': crontab(minute="*"),
    }
}