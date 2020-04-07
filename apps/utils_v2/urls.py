from django.conf.urls import url
from apps.utils_v2 import views

urlpatterns = [
    url(r'^upload_image$', views.UploadImage.as_view(), name='upload_image'),
]
