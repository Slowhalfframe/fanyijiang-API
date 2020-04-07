DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fanyijiang',
        'USER': 'root',
        'PASSWORD': '968168kfyee!!!',
        'HOST': '47.92.28.66',
        'PORT': '3306',
        'CHARSET': ' utf8',
    }
}

# 跨域
CORS_ORIGIN_ALLOW_ALL = True

USER_CENTER_GATEWAY = 'http://47.92.28.66:9233'
PICTURE_HOST = "http://47.92.28.66:9234/public"
FRONT_HOST = 'http://192.168.0.107:9000'

HAYSTACK_CONNECTIONS = {
    'default': {
        # 'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'ENGINE': 'apps.utils.haystack.CustomElasticsearchSearchEngine',
        'URL': 'http://localhost:9200/',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'fanyijiang',  # 指定elasticsearch建立的索引库的名称
    },
}
