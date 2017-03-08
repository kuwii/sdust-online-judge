from django.shortcuts import render, redirect, reverse
from rest_api.models import IDENTITIES as USER_IDENTITIES


class Utils:
    class UserInfo:
        @staticmethod
        def basic(request):
            user = request.user
            if user.is_authenticated():
                identities = set()
                person = user.person
                for name, model in USER_IDENTITIES.items():
                    if model.objects.filter(user=person).exists():
                        identities.add(name)
                info = {
                    'is_authenticated': False,
                    'identities': identities
                }
            else:
                info = {
                    'is_authenticated': False
                }
            return info


class MainPage:
    @staticmethod
    def home(request):
        return render(request, 'homepage.html', {
            'user_info': Utils.UserInfo.basic(request)
        })

    @staticmethod
    def to_home(request):
        if request:
            pass
        return redirect(reverse('web-home'))

    @staticmethod
    def login(request):
        if request.user.is_authenticated():
            return redirect(reverse('homepage'))
        return render(request, 'login.html')
