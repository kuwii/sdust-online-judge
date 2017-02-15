from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import DjangoFilterBackend, SearchFilter, OrderingFilter
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, NotFound
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404


class UserMixin(object):
    username = None

    def get_username(self, request):
        self.username = request.user.username


class ExtraDataMixin(object):
    def __init__(self, *args, **kwargs):
        self.extra_data = {}
        init = getattr(super(), '__init__')
        init(*args, **kwargs)


class UserModelListMixin(CreateModelMixin, ListModelMixin):
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


class UserModelDetailMixin(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
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


class NestedUserModelListMixin(UserModelListMixin):
    def list(self, request, *args, **kwargs):
        set_list_queryset = getattr(self, 'set_list_queryset')
        set_list_queryset(kwargs)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        set_parent = getattr(self, 'set_parent')
        set_parent(kwargs)
        return super().create(request, *args, **kwargs)


class NestedUserModelDetailMixin(UserModelDetailMixin):
    def retrieve(self, request, *args, **kwargs):
        get_parent = getattr(self, 'get_parent')
        parent = get_parent(kwargs)
        get_object = getattr(self, 'get_object')
        instance = get_object()

        parent_name = getattr(self, 'parent_related_name')
        ins_parent = getattr(instance, parent_name)
        if ins_parent != parent:
            raise NotFound

        get_serializer = getattr(self, 'get_serializer')
        serializer = get_serializer(instance)
        return Response(serializer.data)


class FilterViewSet(GenericViewSet):
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)


class CreateListViewSet(CreateModelMixin, ListModelMixin, FilterViewSet):
    pass


class ReadOnlyViewSet(RetrieveModelMixin, ListModelMixin, FilterViewSet):
    pass


class ReadOnlyListViewSet(ListModelMixin, FilterViewSet):
    pass


class ReadOnlyDetailViewSet(RetrieveModelMixin, FilterViewSet):
    pass


class UserModelListViewSet(ExtraDataMixin,
                           UserModelListMixin,
                           FilterViewSet,
                           UserMixin):
    pass


class UserModelDetailViewSet(ExtraDataMixin,
                             UserModelDetailMixin,
                             FilterViewSet,
                             UserMixin):
    pass


class UserModelViewSet(ExtraDataMixin,
                       UserModelListMixin,
                       UserModelDetailMixin,
                       FilterViewSet,
                       UserMixin):
    pass


class NestedUserModelListViewSet(ExtraDataMixin,
                                 NestedUserModelListMixin,
                                 FilterViewSet,
                                 UserMixin,
                                 NestedMixin):
    pass


class NestedUserModelDetailViewSet(ExtraDataMixin,
                                   NestedUserModelDetailMixin,
                                   FilterViewSet,
                                   UserMixin,
                                   NestedMixin):
    pass


class NestedUserModelViewSet(ExtraDataMixin,
                             NestedUserModelListMixin,
                             NestedUserModelDetailMixin,
                             FilterViewSet,
                             UserMixin,
                             NestedMixin):
    pass


class AlreadyLogin(PermissionDenied):
    status_code = HTTP_403_FORBIDDEN
    default_detail = _('Already login.')


class UserDisabled(AuthenticationFailed):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = _('User disabled.')


class PasswordConfirmationField(AuthenticationFailed):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = _('Password confirmation failed..')


def problem_in_client(problem, client):
    cats = problem.categories.all()
    return cats.filter(clients=client).exists()
