from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^(?P<kind>[a-z]+)/(?P<id>\d+)/$", views.VoteView.as_view(), name="root"),
]
