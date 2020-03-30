from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.HomePageRecommendAPIView.as_view(), name="home"),
    url(r"^follows$", views.HomePageFollowContentAPIView.as_view(), name="follows"),
    url(r"^wait_answer$", views.WaitAnswerAPIView.as_view(), name="wait_answer"),
    url(r"^creator$", views.HomePageCreatorAPIView.as_view(), name="creator"),
]
