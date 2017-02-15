"""sdustoj_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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

from rest_api.urls import admin_url_patterns as admin_api_urls, url_patterns as api_urls
from web.urls import url_patterns as web_urls
from web.views import to_home

urlpatterns = [
    url(r'^$', to_home, name='to_home'),
    url(r'^admin/', admin.site.urls),
    url(r'^api-admin/', include(admin_api_urls)),
    url(r'^api/', include(api_urls)),
    url(r'^web/', include(web_urls)),
    url(r'^api-docs/', include('rest_framework_docs.urls')),
    # url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
