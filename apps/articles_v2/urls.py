from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ArticleView.as_view(), name="root"),
]
