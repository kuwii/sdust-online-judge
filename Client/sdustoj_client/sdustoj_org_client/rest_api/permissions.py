from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import IdentityChoices


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated():
            return False
        return user == obj.user
    
    
class UserPermission(BasePermission):
    read_identities = []
    write_identities = []
    site_permission = False

    @staticmethod
    def _user_in_model(user, identity_words):
        profile = user.profile
        for id_str in identity_words:
            if id_str in profile.identities and profile.identities[id_str] is not False:
                return True
        return False

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated():
            return False
        if self.site_permission and user.is_staff is False:
            return False
        if request.method in SAFE_METHODS:
            return self._user_in_model(user, self.read_identities)
        else:
            return self._user_in_model(user, self.write_identities)


class IsRoot(UserPermission):
    read_identities = (IdentityChoices.root, )
    write_identities = (IdentityChoices.root, )
    site_permission = True


class IsUserAdmin(UserPermission):
    read_identities = (IdentityChoices.user_admin, IdentityChoices.root, )
    write_identities = (IdentityChoices.user_admin, IdentityChoices.root, )
    site_permission = True


class IsOrgAdmin(UserPermission):
    read_identities = (IdentityChoices.org_admin, IdentityChoices.root, )
    write_identities = (IdentityChoices.org_admin, IdentityChoices.root, )
    site_permission = True
