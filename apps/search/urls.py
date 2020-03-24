from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    url(r"^$", views.RootView.as_view({"get": "list"}), name="root"),
]

# router = DefaultRouter()
# router.register("", views.UniformSearchViewSet, base_name="uniform_search")
# urlpatterns += router.urls
