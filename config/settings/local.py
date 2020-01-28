from .base import * # noqa
from .base import env


DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "192.168.0.191"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
    'http://localhost:8081',
    'http://localhost'
]
