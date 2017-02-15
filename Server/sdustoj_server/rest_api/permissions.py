from rest_framework.permissions import BasePermission, SAFE_METHODS

GROUP_NAME_ROOT = 'Root'
GROUP_NAME_USER_ADMIN = 'UserAdmin'
GROUP_NAME_PROBLEM_ADMIN = 'ProblemAdmin'
GROUP_NAME_CATEGORY_ADMIN = 'CategoryAdmin'
GROUP_NAME_JUDGE_ADMIN = 'JudgeAdmin'
GROUP_NAME_CLIENT_ADMIN = 'ClientAdmin'
GROUP_NAME_CLIENT = 'Client'


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated():
            return False
        return user.username == obj.username


class UserGroupPermission(BasePermission):
    read_group_names = []
    write_group_names = []

    @staticmethod
    def _user_in_group(user, group_names):
        for name in group_names:
            if user.groups.filter(name=name).exists():
                return True
        return False

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated():
            return False
        if request.method in SAFE_METHODS:
            return self._user_in_group(user, self.read_group_names)
        elif request.method == 'DELETE':
            return self._user_in_group(user, (GROUP_NAME_ROOT,))
        else:
            return self._user_in_group(user, self.write_group_names)


class IsRoot(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT,)
    write_group_names = (GROUP_NAME_ROOT,)


class IsUserAdmin(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT, GROUP_NAME_USER_ADMIN)
    write_group_names = (GROUP_NAME_ROOT, GROUP_NAME_USER_ADMIN)


class IsProblemAdmin(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT, GROUP_NAME_PROBLEM_ADMIN)
    write_group_names = (GROUP_NAME_ROOT, GROUP_NAME_PROBLEM_ADMIN)


class IsCategoryAdmin(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT, GROUP_NAME_PROBLEM_ADMIN, GROUP_NAME_CATEGORY_ADMIN)
    write_group_names = (GROUP_NAME_ROOT, GROUP_NAME_PROBLEM_ADMIN, GROUP_NAME_CATEGORY_ADMIN)


class IsJudgeAdmin(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT, GROUP_NAME_JUDGE_ADMIN)
    write_group_names = (GROUP_NAME_ROOT, GROUP_NAME_JUDGE_ADMIN)


class IsClientAdmin(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT, GROUP_NAME_CLIENT_ADMIN)
    write_group_names = (GROUP_NAME_ROOT, GROUP_NAME_CLIENT_ADMIN)


class ClientReadOnly(UserGroupPermission):
    read_group_names = (GROUP_NAME_ROOT,
                        GROUP_NAME_CLIENT_ADMIN,
                        GROUP_NAME_PROBLEM_ADMIN,
                        GROUP_NAME_CATEGORY_ADMIN,
                        GROUP_NAME_CLIENT, )
    write_group_names = ()


class ClientWriteable(ClientReadOnly):
    write_group_names = (GROUP_NAME_ROOT,
                         GROUP_NAME_CLIENT_ADMIN,
                         GROUP_NAME_PROBLEM_ADMIN,
                         GROUP_NAME_CATEGORY_ADMIN,
                         GROUP_NAME_CLIENT, )
