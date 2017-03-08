# -*- coding: utf-8 -*-
from rest_framework import viewsets, mixins
from datetime import datetime

from .models import Organization
from .models import Person, Student, Teacher, EduAdmin, OrgAdmin, SiteAdmin

from .serializers import OrganizationSerializers, UserSerializers

from .filters import OrganizationFilters, UserFilters
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.settings import api_settings
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from . import permissions


class Utils:
    class Exceptions:
        class UserDisabled(AuthenticationFailed):
            status_code = HTTP_401_UNAUTHORIZED
            default_detail = _('User disabled.')

        class AlreadyLogin(PermissionDenied):
            status_code = HTTP_403_FORBIDDEN
            default_detail = _('Already login.')

    class ViewSets:
        class Mixin:
            class ResourceMixin(object):
                username = None

                def get_username(self, request):
                    user = request.user
                    self.username = request.user.username if user.is_authenticated() else None

            class ExtraDataMixin(object):
                def __init__(self, *args, **kwargs):
                    self.extra_data = {}
                    init = getattr(super(), '__init__')
                    init(*args, **kwargs)

            class ResourceListMixin(mixins.CreateModelMixin, mixins.ListModelMixin):
                def create(self, request, *args, **kwargs):
                    get_username = getattr(self, 'get_username')
                    get_username(request)
                    extra_data = getattr(self, 'extra_data')
                    username = getattr(self, 'username')
                    extra_data['creator'] = username
                    extra_data['updater'] = username
                    return super().create(request, *args, **kwargs)

                def perform_create(self, serializer):
                    extra_data = getattr(self, 'extra_data')
                    instance = serializer.save(**extra_data)
                    return instance

            class ResourceInstanceMixin(mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin, mixins.DestroyModelMixin):
                def update(self, request, *args, **kwargs):
                    get_username = getattr(self, 'get_username')
                    get_username(request)
                    extra_data = getattr(self, 'extra_data')
                    extra_data['updater'] = getattr(self, 'username')
                    return super().update(request, *args, **kwargs)

                def perform_update(self, serializer):
                    extra_data = getattr(self, 'extra_data')
                    instance = serializer.save(**extra_data)
                    return instance

        class ListModelViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
            pass

        class InstanceModelViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                   viewsets.GenericViewSet):
            pass

        class ResourceListViewSet(Mixin.ExtraDataMixin, Mixin.ResourceListMixin, viewsets.GenericViewSet,
                                  Mixin.ResourceMixin):
            pass

        class ResourceInstanceViewSet(Mixin.ExtraDataMixin, Mixin.ResourceInstanceMixin, viewsets.GenericViewSet,
                                    Mixin.ResourceMixin):
            pass

        class ResourceViewSet(Mixin.ExtraDataMixin, Mixin.ResourceListMixin, Mixin.ResourceInstanceMixin,
                              viewsets.GenericViewSet, Mixin.ResourceMixin):
            pass


class OrganizationViewSets:
    class OrganizationAdminViewSet(Utils.ViewSets.ResourceViewSet):
        queryset = Organization.objects.order_by('id')
        serializer_class = OrganizationSerializers.Organization
        permission_classes = (permissions.IsOrgAdmin, )
        filter_class = OrganizationFilters.Organization
        search_fields = ('name', 'id')
        ordering_fields = (
            'id', 'name', 'org_class',
            'number_organizations', 'number_course_meta', 'number_categories',
            'number_users', 'number_admins', 'number_teachers', 'number_students',
            'create_time', 'update_time'
        )

        def perform_create(self, serializer):
            instance = super().perform_create(serializer)
            if instance.parent is not None:
                instance.parent.number_organizations += 1
                instance.parent.save()

        def perform_update(self, serializer):
            parent = serializer.instance.parent
            instance = super().perform_update(serializer)
            if parent != instance.parent:
                if parent is not None:
                    parent.number_organizations -= 1
                parent.save()
                if instance.parent is not None:
                    instance.parent.number_organizations += 1
                    instance.parent.save()

        def perform_destroy(self, instance):
            instance.parent.number_organizations -= 1
            instance.parent.save()
            instance.delete()


class UserViewSets:
    class Person:
        class List:
            class PersonAdminViewSet(Utils.ViewSets.ResourceListViewSet):
                queryset = Person.objects.order_by('id')
                serializer_class = UserSerializers.Person.List
                permission_classes = (permissions.IsUserAdmin, )
                filter_class = UserFilters.Person
                search_fields = ('user', 'name')
                ordering_fields = (
                    'id', 'user', 'name', 'email', 'sex', 'phone', 'email', 'last_login', 'ip',
                    'create_time', 'update_time'
                )

        class Instance:
            class PersonAdminViewSet(Utils.ViewSets.ResourceInstanceViewSet):
                pass

    class LoginViewSet(viewsets.GenericViewSet):
        serializer_class = UserSerializers.Login

        @staticmethod
        def create(request):
            if request.user.is_authenticated():
                raise Utils.Exceptions.AlreadyLogin()

            serializer = UserSerializers.Login(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = request.data['username']
            password = request.data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    user.person.last_login = datetime.now()
                    user.person.save()
                else:
                    raise Utils.Exceptions.UserDisabled()
            else:
                raise AuthenticationFailed

            try:
                headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
            except (TypeError, KeyError):
                headers = {}
            return Response(status=HTTP_200_OK, headers=headers)

    class LogoutViewSet(viewsets.GenericViewSet):
        permission_classes = (IsAuthenticated,)

        @staticmethod
        def list(request):
            logout(request)
            return Response(status=HTTP_200_OK)
