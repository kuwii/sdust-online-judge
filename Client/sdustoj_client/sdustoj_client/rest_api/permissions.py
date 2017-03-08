from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Student, Teacher, EduAdmin, OrgAdmin, UserAdmin, SiteAdmin


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated():
            return False
        return user.username == obj.user


class UserPermission(BasePermission):
    read_models = []
    write_models = []

    @staticmethod
    def _user_in_model(user, models_):
        person = user.person
        for model in models_:
            if model.objects.filter(user=person).exists():
                return True
        return False

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated():
            return False
        if request.method in SAFE_METHODS:
            return self._user_in_model(user, self.read_models)
        else:
            return self._user_in_model(user, self.write_models)


class IsSiteAdmin(UserPermission):
    read_models = (SiteAdmin, )
    write_models = (SiteAdmin, )


class IsUserAdmin(UserPermission):
    read_models = (UserAdmin, SiteAdmin, )
    write_models = (UserAdmin, SiteAdmin, )


class IsOrgAdmin(UserPermission):
    read_models = (OrgAdmin, SiteAdmin, )
    write_models = (OrgAdmin, SiteAdmin, )


class IsEduAdmin(UserPermission):
    read_models = (EduAdmin, OrgAdmin, SiteAdmin)
    write_models = (EduAdmin, OrgAdmin, SiteAdmin)


class IsTeacher(UserPermission):
    read_models = (Teacher, SiteAdmin)
    write_models = (Teacher, SiteAdmin)


class IsStudent(UserPermission):
    read_models = (Student, Teacher, SiteAdmin)
    write_models = (Student, Teacher, SiteAdmin)
