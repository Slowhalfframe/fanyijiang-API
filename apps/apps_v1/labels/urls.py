from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.LabelView.as_view(), name="labels"),
    url(r"^(?P<label_id>\d+)/$", views.LabelDetailView.as_view(), name="label_detail"),
    url(r"^(?P<label_id>\d+)/discussion/$", views.LabelDiscussView.as_view(), name="label_discuss"),
    url(r"^relations/$", views.LabelRelationView.as_view(), name="relations"),
    url(r"^relations/(?P<pk>\d+)$", views.ChildLabelView.as_view(), name="child"),
    url(r"^follows/$", views.LabelFollowView.as_view(), name="follows"),
    url(r"^search/$", views.LabelSearchView.as_view(), name="search"),
    url(r"^wander/$", views.LabelWanderView.as_view(), name="wander"),
    url(r"^advice/$", views.AdviceLabelView.as_view(), name="advice"),
]
