from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.IdeaView.as_view(), name="root"),
]
