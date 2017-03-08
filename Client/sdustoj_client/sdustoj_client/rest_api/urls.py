from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSets, UserViewSets

admin_router = DefaultRouter()
admin_router.register(
    r'organizations', OrganizationViewSets.OrganizationAdminViewSet, base_name='admin-organization'
)

admin_url_patterns = []
admin_url_patterns += admin_router.urls


router = DefaultRouter()
router.register(
    r'login', UserViewSets.LoginViewSet, base_name='api-login'
)
router.register(
    r'logout', UserViewSets.LogoutViewSet, base_name='api-logout'
)

api_url_patterns = []
api_url_patterns += router.urls
