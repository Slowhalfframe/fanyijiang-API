from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.RootView.as_view({"get": "list"}), name="root"),
    url(r"^users/$", views.FindUserView.as_view({"get": "list"}), name="user"),
]
