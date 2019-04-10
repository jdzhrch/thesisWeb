from django.urls import path

from multiDimEvents.models import Event, UserHistory
from . import views

from django.conf.urls import url, include


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^addEvent/$', views.addEvent),
    url(r'^getHistory/$', views.getHistory),
    url(r'^getCategory/$', views.getCategory),
    url(r'^getArticle/$', views.getArticle),
]