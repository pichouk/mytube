"""URL configuration for subscriptions app"""

from django.conf.urls import re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^account/login$', auth_views.LoginView.as_view(template_name='subscriptions/login.html')),
    re_path(r'^account/logout$', auth_views.LogoutView.as_view()),
    re_path(r'^account/change_password$', auth_views.PasswordChangeView.as_view(template_name='subscriptions/change_password.html', success_url='/')),
    re_path(r'^subscriptions/subscribe$', views.subscribe_channel, name='subscribe_channel'),
    re_path(r'^subscriptions/list$', views.list_subscriptions, name='list_subscriptions'),
    re_path(r'^subscriptions/unsubscribe$', views.unsubscribe_channel, name='unsubscribe_channel'),
    re_path(r'^channel/(?P<channel_id>[\w\W]+)$', views.show_channel, name='show_channel'),
    re_path(r'^refresh(?:/(?P<channel_id>[\w\W]+))?/$', views.refresh, name='refresh'),
]
