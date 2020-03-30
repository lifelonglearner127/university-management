from .base import * # noqa
from .base import env


DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["121.42.8.83"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    'http://121.42.8.83',
    'http://121.42.8.83:8080',
]
