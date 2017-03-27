from rest_framework.filters import FilterSet
import django_filters
from . import models


class Utils:
    resource_fields = ('creator', 'create_time', 'updater', 'update_time',
                       'create_time_gte', 'create_time_lte', 'update_time_gte', 'update_time_lte')

    class ResourceFilter(FilterSet):
        create_time_gte = django_filters.DateTimeFilter(name='create_time', lookup_expr='gte')
        create_time_lte = django_filters.DateTimeFilter(name='create_time', lookup_expr='lte')
        update_time_gte = django_filters.DateTimeFilter(name='update_time', lookup_expr='gte')
        update_time_lte = django_filters.DateTimeFilter(name='update_time', lookup_expr='lte')
        creator = django_filters.CharFilter(name='creator')
        updater = django_filters.CharFilter(name='updater')


class OrganizationFilters:
    class Organization(Utils.ResourceFilter):
        number_organizations_gte = django_filters.NumberFilter(name='number_organizations', lookup_expr='gte')
        number_admins_gte = django_filters.NumberFilter(name='number_admins', lookup_expr='gte')
        number_teachers_gte = django_filters.NumberFilter(name='number_teachers', lookup_expr='gte')
        number_students_gte = django_filters.NumberFilter(name='number_students', lookup_expr='gte')
        number_organizations_lte = django_filters.NumberFilter(name='number_organizations', lookup_expr='lte')
        number_admins_lte = django_filters.NumberFilter(name='number_admins', lookup_expr='lte')
        number_teachers_lte = django_filters.NumberFilter(name='number_teachers', lookup_expr='lte')
        number_students_lte = django_filters.NumberFilter(name='number_students', lookup_expr='lte')

        class Meta:
            model = models.Organization
            fields = (
                'id', 'name', 'caption', 'parent',
                'number_organizations', 'number_organizations_gte', 'number_organizations_lte',
                'number_admins', 'number_admins_gte', 'number_admins_lte',
                'number_teachers', 'number_teachers_gte', 'number_teachers_lte',
                'number_students', 'number_students_gte', 'number_students_lte'
            ) + Utils.resource_fields


class UserFilters:
    class UserProfile(Utils.ResourceFilter):
        last_login_gte = django_filters.DateTimeFilter(name='last_login', lookup_expr='gte')
        last_login_lte = django_filters.DateTimeFilter(name='last_login', lookup_expr='lte')

        class Meta:
            model = models.UserProfile
            fields = (
                'username', 'name', 'sex', 'phone', 'email',
                'last_login', 'last_login_gte', 'last_login_lte', 'ip'
            ) + Utils.resource_fields
