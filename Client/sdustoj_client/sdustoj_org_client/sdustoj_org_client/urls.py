"""sdustoj_org_client URL Configuration

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

from rest_api.urls import admin_url_patterns, api_url_patterns
from web.urls import url_patterns
from web.views import MainPages

urlpatterns = [
    url(r'^JudgeOnline/$', MainPages.to_home, name='web-to-home'),
    url(r'^JudgeOnline/web/', include(url_patterns)),
    url(r'^JudgeOnline/api/', include(api_url_patterns)),
    url(r'^JudgeOnline/api-admin/', include(admin_url_patterns)),
]
