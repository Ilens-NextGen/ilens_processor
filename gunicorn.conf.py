from src.utils import getenv, getenvbool, getintenv

workers = getintenv('GUNICORN_WORKERS', 1)
host = getenv('HOST', 'localhost')
port = getintenv('PORT', 8000)
bind = getenv('GUNICORN_BIND', f"{host}:{port}")
reload = getenvbool('GUNICORN_RELOAD', False)
accesslog = getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = getenv('GUNICORN_ERROR_LOG', '-')
loglevel = getenv('GUNICORN_LOG_LEVEL', 'info')
timeout = getintenv('GUNICORN_TIMEOUT', 30)
worker_class = getenv('GUNICORN_WORKER_CLASS')
wsgi_app = getenv('AIO_APP')
