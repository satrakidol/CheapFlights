from . import create_app
import project.celeryconfig as celeryconfig


flask_app = create_app()
celery_app = flask_app.extensions["celery"]
celery_app.config_from_object(celeryconfig)
