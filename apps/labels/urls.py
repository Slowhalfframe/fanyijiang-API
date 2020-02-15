from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.LabelView.as_view(), name="labels"),
]
