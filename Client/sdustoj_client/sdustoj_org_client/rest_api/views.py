# -*- coding: utf-8 -*-
from rest_framework import viewsets, mixins, status, exceptions, response, permissions as permissions_
from . import models, serializers, permissions, filters

from rest_framework.settings import api_settings

from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404


class Utils:
    class Exceptions:
        class UserDisabled(exceptions.AuthenticationFailed):
            status_code = status.HTTP_401_UNAUTHORIZED
            default_detail = _('User disabled.')

        class AlreadyLogin(exceptions.PermissionDenied):
            status_code = status.HTTP_403_FORBIDDEN
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
                def set_user_info(self, request):
                    get_username = getattr(self, 'get_username')
                    get_username(request)
                    extra_data = getattr(self, 'extra_data')
                    username = getattr(self, 'username')
                    extra_data['creator'] = username
                    extra_data['updater'] = username

                def create(self, request, *args, **kwargs):
                    self.set_user_info(request)
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

            class NestedMixin(object):
                parent_queryset = None  # 父类的查询集
                parent_lookup = None  # 在视图类中传递的参数中代表父类的参数的名字
                parent_related_name = None  # 子类中连接父类的外键名
                parent_pk_field = None  # 父类的主键

                def get_parent(self, kwargs):
                    if self.parent_lookup is not None:
                        lookup_value = kwargs.get(self.parent_lookup)
                        if lookup_value is not None:
                            parent = get_object_or_404(self.parent_queryset, **{self.parent_pk_field: lookup_value})
                            return parent
                    return None

                def set_list_queryset(self, kwargs):
                    parent = self.get_parent(kwargs)
                    if parent is not None:
                        queryset = getattr(self, 'queryset')
                        setattr(self, 'queryset', queryset.filter(**{self.parent_related_name: parent}))

                def set_parent(self, kwargs):
                    parent = self.get_parent(kwargs)
                    extra_data = getattr(self, 'extra_data')
                    extra_data[self.parent_related_name] = parent

            class NestedResourceListMixin(ResourceListMixin):
                def list(self, request, *args, **kwargs):
                    set_list_queryset = getattr(self, 'set_list_queryset')
                    set_list_queryset(kwargs)
                    return super().list(request, *args, **kwargs)

                def create(self, request, *args, **kwargs):
                    set_parent = getattr(self, 'set_parent')
                    set_parent(kwargs)
                    return super().create(request, *args, **kwargs)

            class NestedResourceInstanceMixin(ResourceInstanceMixin):
                def retrieve(self, request, *args, **kwargs):
                    get_parent = getattr(self, 'get_parent')
                    parent = get_parent(kwargs)
                    get_object = getattr(self, 'get_object')
                    instance = get_object()

                    parent_name = getattr(self, 'parent_related_name')
                    ins_parent = getattr(instance, parent_name)
                    if ins_parent != parent:
                        raise exceptions.NotFound

                    get_serializer = getattr(self, 'get_serializer')
                    serializer = get_serializer(instance)
                    return response.Response(serializer.data)

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

        class NestedResourceListViewSet(Mixin.ExtraDataMixin,
                                        Mixin.NestedResourceListMixin,
                                        viewsets.GenericViewSet,
                                        Mixin.ResourceMixin,
                                        Mixin.NestedMixin):
            pass

        class NestedResourceDetailViewSet(Mixin.ExtraDataMixin,
                                          Mixin.NestedResourceInstanceMixin,
                                          viewsets.GenericViewSet,
                                          Mixin.ResourceMixin,
                                          Mixin.NestedMixin):
            pass

        class NestedResourceViewSet(Mixin.ExtraDataMixin,
                                    Mixin.NestedResourceListMixin,
                                    Mixin.NestedResourceInstanceMixin,
                                    viewsets.GenericViewSet,
                                    Mixin.ResourceMixin,
                                    Mixin.NestedMixin):
            pass


class UserViewSets(object):
    """
    与用户管理相关的ViewSet。
    """
    class Admin(object):
        class List(object):
            class AdminAdminViewSet(Utils.ViewSets.ResourceListViewSet):
                queryset = models.UserProfile.objects.filter(is_staff=True).order_by('user')
                serializer_class = serializers.UserSerializers.Admin.ListAdmin
                permission_classes = (permissions.IsUserAdmin, )
                filter_class = filters.UserFilters.UserProfile
                search_fields = ('username', 'name',)
                ordering_fields = ('username', 'name', 'sex', 'phone', 'email', 'last_login',
                                   'creator', 'create_time', 'updater', 'update_time',)

                def create(self, request, *args, **kwargs):
                    identities = request.user.profile.identities
                    root = models.IdentityChoices.root
                    if root in identities and identities[root] is True:
                        self.serializer_class = serializers.UserSerializers.Admin.ListRoot
                    return super().create(request, *args, **kwargs)

        class Instance(object):
            class AdminAdminViewSet(Utils.ViewSets.ResourceInstanceViewSet):
                queryset = models.UserProfile.objects.filter(is_staff=True).order_by('user')
                serializer_class = serializers.UserSerializers.Admin.InstanceAdmin
                permission_classes = (permissions.IsUserAdmin, )
                lookup_field = 'username'

                def update(self, request, *args, **kwargs):
                    identities = request.user.profile.identities
                    root = models.IdentityChoices.root
                    if root in identities and identities[root] is True:
                        self.serializer_class = serializers.UserSerializers.Admin.InstanceRoot
                    return super().update(request, *args, **kwargs)

    class User(object):
        class List(object):
            class UserAdminViewSet(Utils.ViewSets.ResourceListViewSet):
                queryset = models.UserProfile.objects.order_by('user')
                serializer_class = serializers.UserSerializers.User.ListAdmin
                permission_classes = (permissions.IsUserAdmin, )
                filter_class = filters.UserFilters.UserProfile
                search_fields = ('username', 'name',)
                ordering_fields = ('username', 'name', 'sex', 'phone', 'email', 'last_login',
                                   'creator', 'create_time', 'updater', 'update_time',)

                def create(self, request, *args, **kwargs):
                    identities = request.user.profile.identities
                    root = models.IdentityChoices.root
                    if root in identities and identities[root] is True:
                        self.serializer_class = serializers.UserSerializers.User.ListRoot
                    return super().create(request, *args, **kwargs)

        class Instance(object):
            class UserAdminViewSet(Utils.ViewSets.ResourceInstanceViewSet):
                queryset = models.UserProfile.objects.order_by('user')
                serializer_class = serializers.UserSerializers.User.InstanceAdmin
                permission_classes = (permissions.IsUserAdmin, )
                lookup_field = 'username'

                def update(self, request, *args, **kwargs):
                    identities = request.user.profile.identities
                    root = models.IdentityChoices.root
                    if root in identities and identities[root] is True:
                        self.serializer_class = serializers.UserSerializers.User.InstanceRoot
                    return super().update(request, *args, **kwargs)

    class Self(object):
        """
        用户用于查看和修改自己信息的ViewSet。
        """
        class UserViewSet(Utils.ViewSets.InstanceModelViewSet):
            queryset = models.UserProfile
            serializer_class = serializers.UserSerializers.Self.Instance
            permission_classes = (permissions.IsSelf, )
            lookup_field = 'username'

    class LoginViewSet(viewsets.GenericViewSet):
        serializer_class = serializers.UserSerializers.Login

        @staticmethod
        def create(request):
            if request.user.is_authenticated():
                raise Utils.Exceptions.AlreadyLogin()

            serializer = serializers.UserSerializers.Login(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = request.data['username']
            password = request.data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    user.profile.last_login = timezone.now()
                    if 'HTTP_X_FORWARDED_FOR' in request.META:
                        ip = request.META['HTTP_X_FORWARDED_FOR']
                    else:
                        ip = request.META['REMOTE_ADDR']
                    user.profile.ip = ip
                    user.profile.save()
                else:
                    raise Utils.Exceptions.UserDisabled()
            else:
                raise exceptions.AuthenticationFailed

            try:
                headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
            except (TypeError, KeyError):
                headers = {}
            return response.Response(status=status.HTTP_200_OK, headers=headers)

    class LogoutViewSet(viewsets.GenericViewSet):
        permission_classes = (permissions_.IsAuthenticated,)

        @staticmethod
        def list(request):
            logout(request)
            return response.Response(status=status.HTTP_200_OK)


class OrgViewSets(object):
    """
    与机构相关的ViewSet。
    """
    class Organization(object):
        class List(object):
            class OrganizationAdminViewSet(Utils.ViewSets.ResourceListViewSet):
                queryset = models.Organization.objects.exclude(name='ROOT').order_by('id')
                serializer_class = serializers.OrgSerializers.Organization.ListAdmin
                permission_classes = (permissions.IsOrgAdmin, )
                filter_class = filters.OrganizationFilters.Organization
                search_fields = ('name', 'caption', )
                ordering_fields = ('id', 'name', 'caption', 'parent',
                                   'number_organizations', 'number_students', 'number_teachers', 'number_admins')
                lookup_field = 'id'

                def perform_create(self, serializer):
                    instance = super().perform_create(serializer)
                    instance.parent.number_organizations += 1
                    instance.parent.save()
                    return instance

        class Instance(object):
            class OrganizationAdminViewSet(Utils.ViewSets.ResourceInstanceViewSet):
                queryset = models.Organization.objects.exclude(name='ROOT')
                serializer_class = serializers.OrgSerializers.Organization.InstanceAdmin
                permission_classes = (permissions.IsOrgAdmin, )
                lookup_field = 'id'

                def perform_update(self, serializer):
                    instance = serializer.instance
                    instance.parent.number_organizations -= 1
                    instance.parent.save()
                    instance = super().perform_update(serializer)
                    instance.parent.number_organizations += 1
                    instance.parent.save()
                    return instance

                def perform_destroy(self, instance):
                    instance.parent.number_organizations -= 1
                    instance.parent.save()
                    super().perform_destroy(instance)

    class EduAdmin(object):
        class List(object):
            class EduAdminAdminViewSet(Utils.ViewSets.NestedResourceListViewSet):
                queryset = models.EduAdmin.objects
                serializer_class = serializers.OrgSerializers.EduAdmin.ListAdmin
                permission_classes = (permissions.IsOrgAdmin, )

                parent_queryset = models.Organization.objects
                parent_lookup = 'organization_id'
                parent_related_name = 'organization'
                parent_pk_field = 'id'
