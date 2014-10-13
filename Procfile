web: gunicorn --pythonpath src cobble.wsgi --log-file -
worker: cd src && python manage.py celery worker -B -l info
