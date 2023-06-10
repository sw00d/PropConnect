# /tmp/nginx.socket is where heroku nginx buildpack listens
web: bin/start-nginx uvicorn asgi:application --uds /tmp/nginx.socket --app-dir src/backend
release: ./manage.py migrate --pythonpath src/backend

worker: cd src/backend && celery -A settings.celeryconf worker -l INFO -B --max-tasks-per-child 128 --concurrency 2
