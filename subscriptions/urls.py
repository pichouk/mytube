"""URL configuration for subscriptions app"""

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^account/login$', auth_views.LoginView.as_view(template_name='subscriptions/login.html')),
    url(r'^account/logout$', auth_views.LogoutView.as_view()),
    url(r'^account/change_password$', auth_views.PasswordChangeView.as_view(template_name='subscriptions/change_password.html', success_url='/')),
    url(r'^subscriptions/subscribe$', views.subscribe_channel, name='subscribe_channel'),
    url(r'^subscriptions/list$', views.list_subscriptions, name='list_subscriptions'),
    url(r'^subscriptions/unsubscribe$', views.unsubscribe_channel, name='unsubscribe_channel'),
    url(r'^refresh(?:/(?P<channel_id>[\w\W]+))?/$', views.refresh, name='refresh'),
]
