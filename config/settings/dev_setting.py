import os
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'CHARSET':' utf8',
    }
}


# 缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
           "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 跨域
CORS_ORIGIN_ALLOW_ALL = True


USER_CENTER_GATEWAY = 'http://localhost:9233'