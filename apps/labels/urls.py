from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.LabelView.as_view(), name="labels"),
    url(r"^relations/$", views.LabelRelationView.as_view(), name="relations"),
    url(r"^relations/(?P<pk>\d+)$", views.ChildLabelView.as_view(), name="child"),
    url(r"^follows/$", views.LabelFollowView.as_view(), name="follows")
]
