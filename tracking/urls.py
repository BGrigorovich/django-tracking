from django.conf.urls import url
from django.conf import settings
from . import views

urlpatterns = (
    '',
    url(r'^refresh/$', views.update_active_users, name='tracking-refresh-active-users'),
    url(r'^refresh/json/$', views.get_active_users, name='tracking-get-active-users'),
)

if getattr(settings, 'TRACKING_USE_GEOIP', False):
    urlpatterns += (
        '',
        url(r'^map/$', views.display_map, name='tracking-visitor-map'),
    )
