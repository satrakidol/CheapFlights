from project.make_celery import celery_app as celery

@celery.task()
def print_hello():
    print("Hello from task")