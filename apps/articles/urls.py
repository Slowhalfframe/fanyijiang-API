from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ArticleView.as_view(), name="root"),
    url(r"^(?P<article_id>\d+)/$", views.OneArticleView.as_view(), name="one_article"),
    url(r"^drafts/$", views.DraftView.as_view(), name="draft_root"),
    url(r"^(?P<article_id>\d+)/follow/$", views.ArticleFollowView.as_view(), name="follow"),
    url(r"^follow/$", views.ArticleFollowView.as_view(), name="his_follow"),
    # TODO 临时占位的空路由
    url(r"^(?P<article_id>\d+)/comments/$", views.ArticleCommentDetailView.as_view(), name="article_comments"),
    url(r"^(?P<article_id>\d+)/recommend/$", views.ArticleRecommendView.as_view(), name="article_recommend"),
]
