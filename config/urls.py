"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r"^api/labels/", include("apps.labels.urls", namespace="labels")),
    url(r"^api/questions/", include("apps.questions.urls", namespace="questions")),
    url(r"^api/userpage/", include("apps.userpage.urls", namespace="userpage")),
    url(r"^api/articles/", include("apps.articles.urls", namespace="articles")),
    url(r"^api/creator/", include("apps.creator.urls", namespace="creator")),
    url(r'^api/', include('apps.utils.urls', namespace='utils')),

    url(r'public/(?P<path>.*)$', serve, {'document_root': settings.DATA_DIR}),
]
