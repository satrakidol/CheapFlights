# install requirements
```bash
python -m venv testvenv
source testvenv/bin/activate
pip install -r requirements.txt
```

## run flask
```bash
python -m flask --app project run --debug
```

## run celery
```bash
docker run --net=host -d  redis
celery -A project.make_celery worker --loglevel INFO
celery -A project.make_celery beat --loglevel INFO

```


