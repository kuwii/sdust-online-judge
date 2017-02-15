from django.apps import AppConfig
from django.db.models.signals import post_migrate


def check_group(group_name):
    from django.contrib.auth.models import Group
    print(' ... Checking group named ' + group_name + '...', end='')
    if Group.objects.filter(name=group_name).exists():
        print(' done')
    else:
        print(' group does not exist')
        print('Creating group ...')
        group = Group(name=group_name)
        group.save()
        print('Done')


def check_groups():
    from .permissions import GROUP_NAME_ROOT
    from .permissions import GROUP_NAME_PROBLEM_ADMIN, GROUP_NAME_CATEGORY_ADMIN
    from .permissions import GROUP_NAME_JUDGE_ADMIN, GROUP_NAME_CLIENT_ADMIN, GROUP_NAME_USER_ADMIN
    from .permissions import GROUP_NAME_CLIENT
    check_group(GROUP_NAME_ROOT)
    check_group(GROUP_NAME_PROBLEM_ADMIN)
    check_group(GROUP_NAME_CATEGORY_ADMIN)
    check_group(GROUP_NAME_JUDGE_ADMIN)
    check_group(GROUP_NAME_CLIENT_ADMIN)
    check_group(GROUP_NAME_USER_ADMIN)
    check_group(GROUP_NAME_CLIENT)


def check_init_user():
    from django.contrib.auth.models import User, Group
    from config import INIT_USER_SETTINGS
    from .permissions import GROUP_NAME_ROOT
    print('Checking initial user ...', end='')
    if INIT_USER_SETTINGS is None:
        print(' skipped')
    elif User.objects.filter(username=INIT_USER_SETTINGS['username']).exists():
        print(' done')
    else:
        print(' initial user does not exist')
        print('Creating initial user ...')
        user = User(username=INIT_USER_SETTINGS['username'])
        user.set_password(INIT_USER_SETTINGS['password'])
        user.first_name = INIT_USER_SETTINGS.get('first_name', '氏')
        user.last_name = INIT_USER_SETTINGS.get('last_name', '无名')
        user.email = INIT_USER_SETTINGS.get('email', 'Unknown')
        user.is_staff = True
        user.save()
        user.groups.add(Group.objects.get(name=GROUP_NAME_ROOT))
        print(' done')


def callback(sender, **kwargs):
    check_groups()
    check_init_user()


class RestApiConfig(AppConfig):
    name = 'rest_api'

    def ready(self):
        post_migrate.connect(callback, sender=self)
