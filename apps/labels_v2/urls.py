from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.LabelView.as_view(), name="root"),
    url(r"^(?P<label_id>\d+)/$", views.OneLabelView.as_view(), name="one_label"),
    url(r"^(?P<label_id>\d+)/parents/$", views.ParentLabelView.as_view(), name="parent"),
    url(r"^(?P<label_id>\d+)/children/$", views.ChildLabelView.as_view(), name="child"),
    url(r"^(?P<label_id>\d+)/discussion/$", views.LabelDiscussionView.as_view(), name="discussion"),
    url(r"^(?P<label_id>\d+)/follow/$", views.LabelFollowView.as_view(), name="follow"),
    url(r"^follow/$", views.LabelFollowView.as_view(), name="his_follow"),
]
