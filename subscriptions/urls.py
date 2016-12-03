from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^add$', views.add_channel, name='add_channel'),
    url(r'^refresh/(?P<id_channel>[\w\W]+)$', views.refresh, name='refresh'),  # Vue d'un article
]
