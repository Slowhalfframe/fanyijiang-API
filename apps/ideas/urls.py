from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.IdeaView.as_view(), name="ideas"),
    url(r"^(?P<idea_pk>\d+)/$", views.MonoIdeaView.as_view(), name="mono_idea"),
    url(r"^(?P<idea_pk>\d+)/comments/$", views.IdeaCommentView.as_view(), name="comments"),
]
