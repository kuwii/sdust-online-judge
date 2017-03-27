from django.conf.urls import url, include
from .views import MainPages, UserPages, SelfPages, OrgPages


personal_patterns = [
    url(r'^info/', SelfPages.info, name='web-personal-info'),
    url(r'^password/', SelfPages.password, name='web-personal-password'),
]


admin_patterns = [
    url(r'^$', UserPages.AdminAdmin.list, name='web-admins'),
    url(r'^create/', UserPages.AdminAdmin.create, name='web-admins-create'),
    url(r'^info/(\S+)/', UserPages.AdminAdmin.instance, name='web-admins-instance')
]

user_patterns = [
    url(r'^$', UserPages.UserAdmin.list, name='web-users'),
    url(r'^create/', UserPages.UserAdmin.create, name='web-users-create'),
    url(r'^info/(\S+)/', UserPages.UserAdmin.instance, name='web-users')
]

org_admin_patterns = [
    url(r'^$', OrgPages.list, name='web-orgs'),
    url(r'^create/', OrgPages.create, name='web-orgs-create'),
    url(r'^(\d+)/', OrgPages.instance, name='web-orgs-instance')
]

url_patterns = [
    url(r'^home/', MainPages.home, name='web-home'),
    url(r'^login/', MainPages.login, name='web-login'),
    url(r'^personal/', include(personal_patterns)),
    url(r'^users/', include(user_patterns)),
    url(r'^admins/', include(admin_patterns)),
    url(r'^organizations/', include(org_admin_patterns)),
]
