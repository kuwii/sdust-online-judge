from django.conf.urls import url, include
from .views import MainPages, PersonalPages


personal_patterns = [
    url(r'^info/', PersonalPages.info, name='web-personal-info'),
    url(r'^password/', PersonalPages.password, name='web-personal-password'),
]


url_patterns = [
    url(r'home/', MainPages.home, name='web-home'),
    url(r'login/', MainPages.login, name='web-login'),
    url(r'^personal/', include(personal_patterns)),
]
