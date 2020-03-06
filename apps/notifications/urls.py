from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.NotificationAPIView.as_view(), name='notifications')
]