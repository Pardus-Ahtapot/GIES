from django.conf.urls import url
from allow.views import *


urlpatterns = [
    url(r'^create/$', create_request, name='create_request'),
    url(r'^show/$', show_requests, name='show_requests'),
    url(r'^confirm/$', confirm_request, name='confirm_request'),
    url(r'^config/$', show_config, name='show_config'),
    url(r'^setconfig/$', set_config, name='set_config'),
    url(r'^reject/(?P<request_id>\d+)/$', reject_request, name='reject_request'),
]
