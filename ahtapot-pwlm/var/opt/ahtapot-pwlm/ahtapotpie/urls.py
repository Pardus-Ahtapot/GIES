"""ahtapotpie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
import allow.urls as allow_urls
import auth.urls as auth_urls
from allow.views import home
import jet.urls

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^jet/', include(jet.urls, 'jet')),
    url(r'^admin/', admin.site.urls),
    url(r'^request/', include(allow_urls)),
    url(r'^auth/', include(auth_urls)),
]
