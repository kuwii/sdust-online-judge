from rest_framework.filters import FilterSet
from .models import MetaProblem, Description, Sample, TestData, Environment
from .models import Problem, ProblemTestData, Limit, InvalidWord, SpecialJudge
from .models import Submission

from django.contrib.auth.models import User
import django_filters


# == Utils =============================================================================================================

class ResourceFilter(FilterSet):
    create_time_gte = django_filters.DateTimeFilter(name='create_time', lookup_expr='gte')
    create_time_lte = django_filters.DateTimeFilter(name='create_time', lookup_expr='lte')
    update_time_gte = django_filters.DateTimeFilter(name='update_time', lookup_expr='gte')
    update_time_lte = django_filters.DateTimeFilter(name='update_time', lookup_expr='lte')
    creator = django_filters.CharFilter(name='creator')
    updater = django_filters.CharFilter(name='updater')

    resource_fields = ('create_time', 'update_time', 'creator', 'updater')

_RESOURCE_ORDERING = ('create_time', 'update_time', 'creator', 'updater')


# == Meta Problem ======================================================================================================
class MetaProblemFilters:
    class MetaProblemAdminFilter(ResourceFilter):
        class Meta:
            model = MetaProblem
            fields = ResourceFilter.resource_fields + ('id',)

    class DescriptionAdminFilter(ResourceFilter):
        class Meta:
            model = Description
            fields = ResourceFilter.resource_fields + ('id',)

    class SampleAdminFilter(ResourceFilter):
        class Meta:
            model = Sample
            fields = ResourceFilter.resource_fields + ('id',)

    class TestDataAdminFilter(ResourceFilter):
        class Meta:
            model = TestData
            fields = ResourceFilter.resource_fields + ('id',)

    class Problem:
        class ProblemAdminFilter(ResourceFilter):
            class Meta:
                model = Problem
                fields = ResourceFilter.resource_fields + ('id',)

        class TestDataRelAdminFilter(ResourceFilter):
            class Meta:
                model = ProblemTestData
                fields = ResourceFilter.resource_fields + ('id',)

        class LimitAdminFilter(ResourceFilter):
            class Meta:
                model = Limit
                fields = ResourceFilter.resource_fields + ('id',
                                                           'time_limit', 'memory_limit', 'length_limit')

        class InvalidWordAdminFilter(ResourceFilter):
            class Meta:
                model = InvalidWord
                fields = ResourceFilter.resource_fields + ('id', 'word')

        class SpecialJudgeAdminFilter(ResourceFilter):
            class Meta:
                model = SpecialJudge
                fields = ResourceFilter.resource_fields + ('id',)


# == Submission ========================================================================================================

class SubmissionFilters:
    class SubmissioinAdminFilter(FilterSet):
        submit_time_gte = django_filters.DateTimeFilter(name='submit_time', lookup_expr='gte')
        submit_time_lte = django_filters.DateTimeFilter(name='submit_time', lookup_expr='lte')
        update_time_gte = django_filters.DateTimeFilter(name='update_time', lookup_expr='gte')
        update_time_lte = django_filters.DateTimeFilter(name='update_time', lookup_expr='lte')
        time_gte = django_filters.NumberFilter(name='time', lookup_expr='gte')
        time_lte = django_filters.NumberFilter(name='time', lookup_expr='lte')
        memory_gte = django_filters.NumberFilter(name='memory', lookup_expr='gte')
        memory_lte = django_filters.NumberFilter(name='memory', lookup_expr='lte')
        length_gte = django_filters.NumberFilter(name='length', lookup_expr='gte')
        length_lte = django_filters.NumberFilter(name='length', lookup_expr='lte')

        class Meta:
            model = Submission
            fields = ('submit_time', 'update_time', 'time', 'memory', 'length', 'id', 'problem', 'environment',
                      'user', 'contest', 'judge')


# == Environment =======================================================================================================

class EnvironmentAdminFilter(ResourceFilter):
    class Meta:
        model = Environment
        fields = ResourceFilter.resource_fields + ('id',)


# == User ==============================================================================================================

class UserAdminFilter(FilterSet):
    date_joined_gte = django_filters.DateTimeFilter(name='date_joined', lookup_expr='gte')
    date_joined_lte = django_filters.DateTimeFilter(name='date_joined', lookup_expr='lte')
    last_login_gte = django_filters.DateTimeFilter(name='last_login', lookup_expr='gte')
    last_login_lte = django_filters.DateTimeFilter(name='last_login', lookup_expr='lte')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_active',
                  'date_joined_gte', 'date_joined_lte',
                  'last_login_gte', 'last_login_lte')
