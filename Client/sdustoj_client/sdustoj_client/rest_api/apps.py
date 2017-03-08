from django.apps import AppConfig
from django.db.models.signals import post_migrate


def check_init_user():
    from django.contrib.auth.models import User
    from .models import Person, SiteAdmin
    from config import INIT_USER_SETTINGS
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
        user.is_staff = True
        user.save()
        person = Person(user=user)
        if 'name' in INIT_USER_SETTINGS:
            person.name = INIT_USER_SETTINGS['name']
        person.save()
        site_admin = SiteAdmin(user=person)
        site_admin.save()
        print(' done')


def callback(sender, **kwargs):
    check_init_user()


class RestApiConfig(AppConfig):
    name = 'rest_api'

    def ready(self):
        post_migrate.connect(callback, sender=self)
