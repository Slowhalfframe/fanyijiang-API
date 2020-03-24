from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = []

router = DefaultRouter()
router.register("", views.QuestionSearchViewSet, base_name="question_search")
urlpatterns += router.urls
