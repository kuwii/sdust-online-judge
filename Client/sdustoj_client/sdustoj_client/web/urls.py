from django.conf.urls import url
from .views import MainPage

url_patterns = [
    url(r'^home/', MainPage.home, name='web-home'),
    url(r'^login/', MainPage.login, name='web-login'),
]
