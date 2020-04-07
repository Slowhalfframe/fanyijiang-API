from django.conf.urls import url
from apps.utils import views

urlpatterns = [
    url(r'^upload_image$', views.UploadImage.as_view(), name='upload_image'),
]
