import os
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fanyijiang',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'CHARSET':' utf8',
    }
}



# 跨域
CORS_ORIGIN_ALLOW_ALL = True


USER_CENTER_GATEWAY = 'http://localhost:9233'