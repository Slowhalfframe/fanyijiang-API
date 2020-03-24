import os

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
        'CHARSET': 'utf8',
    }
}

# 跨域
CORS_ORIGIN_ALLOW_ALL = True

USER_CENTER_GATEWAY = 'http://47.92.28.66:9233'

PICTURE_HOST = "http://47.92.28.66:9234/public"
