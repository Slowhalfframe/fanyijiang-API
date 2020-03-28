from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^(?P<kind>[a-z]+)/(?P<id>\d+)/$", views.CommentView.as_view(), name="root"),
    url(r"^(?P<comment_id>\d+)/$", views.OneCommentView.as_view(), name="one_comment"),
]
