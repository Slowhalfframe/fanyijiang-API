from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.CreatorHomeAPIView.as_view(), name="home"),
    url(r"^creator_data$", views.CreatorDataDetailAPIView.as_view(), name="creator_data"),
    url(r"^statistics_date_content$", views.StatisticsDateAPIView.as_view(), name="statistics_date_content"),
    url(r"^single_content$", views.SingleDataStatisticsAPIView.as_view(), name="single_content"),
    url(r"^recommend_question$", views.RecommendQuestionAPIVIew.as_view(), name="recommend_question"),
    url(r"^creator_list$", views.CreatorListAPIView.as_view(), name="creator_list"),

]
