from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ArticleView.as_view(), name="root"),
    url(r"^(?P<article_id>\d+)/$", views.OneArticleView.as_view(), name="one_article"),
    url(r"^drafts/$", views.DraftView.as_view(), name="draft_root"),
]
