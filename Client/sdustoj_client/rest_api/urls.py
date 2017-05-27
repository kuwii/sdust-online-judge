from rest_framework import routers

from .views import PersonalViewSets


api_router = routers.DefaultRouter()

api_router.register(
    r'login', PersonalViewSets.Login.LoginViewSet, base_name='api-login')
api_router.register(
    r'logout', PersonalViewSets.Logout.LogoutViewSet, base_name='api-logout')
api_router.register(
    r'personal-info', PersonalViewSets.Personal.PersonalViewSet, base_name='api-personal-info')
api_router.register(
    r'personal-password', PersonalViewSets.Personal.PasswordViewSet, base_name='api-personal-password')

api_patterns = []
api_patterns += api_router.urls
