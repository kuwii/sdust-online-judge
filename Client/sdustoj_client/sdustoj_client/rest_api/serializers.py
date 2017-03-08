from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from . import models


class Utils:
    read_only_fields = ('creator', 'create_time', 'updater', 'update_time')


class OrganizationSerializers:
    class Organization(serializers.ModelSerializer):
        def validate_org_class(self, value):
            def error_change_without_changing_parent():
                raise serializers.ValidationError(
                    'Can not change class of an organization without changing its parent.'
                )

            instance = self.instance
            if instance is not None:
                # 如果更新数据，检查母机构和机构等级变动情况
                if instance.children.exists() and instance.org_class != value:
                    # 如果有子机构且要修改机构等级时，会破坏机构之间的等级关系，故需要禁止
                    raise serializers.ValidationError(
                        'Can not change class of an organization when it has any child.'
                    )

                # 如果不修改母机构且要修改机构等级时，会破坏机构之间的等级关系，故需要禁止
                # 如果修改母机构，则再在parent处检查合法性。
                if ('parent' not in self.initial_data and instance.org_class != value) or ():
                    # 如果提交数据不包含母机构，则必定不会修改母机构
                    error_change_without_changing_parent()
                else:
                    # 如果提交数据包含母机构，则需要验证是否修改了母机构
                    parent_id = self.initial_data['parent']
                    if parent_id == '' or parent_id is None:
                        if instance.parent is None and instance.org_class != value:
                            error_change_without_changing_parent()
                    elif isinstance(parent_id, str) and (not parent_id.isdigit()):
                        return value
                    else:
                        parent = models.Organization.objects.filter(id=int(parent_id)).first()
                        if parent is None:
                            return value
                        if parent == instance.parent and instance.org_class != value:
                            error_change_without_changing_parent()

            if not (value == 1 or value == 2 or value == 3):
                raise serializers.ValidationError('This field can only be 1, 2 or 3.')

            return value

        def validate_parent(self, value):
            instance = self.instance
            org_class = int(self.initial_data.get('org_class', 0))
            if instance is not None:
                if value != instance.parent:
                    # 如果要修改母机构，进行检查
                    if 'org_class' not in self.initial_data:
                        # 如果修改母机构时没有指定机构等级，则以现有机构等级进行判断
                        self.validate_org_class(instance.org_class)
                        org_class = instance.org_class
                if value == instance:
                    raise serializers.ValidationError('Parent can not be itself.')

            if org_class == 1 and (value is not None):
                raise serializers.ValidationError('Primary organization has no parent.')
            if org_class != 1 and (value is None):
                raise serializers.ValidationError('Secondary or sub organization must have a parent.')
            if org_class != 1 and (org_class - value.org_class != 1):
                raise serializers.ValidationError('Class of parent must be exactly 1 smaller than itself.')

            return value

        class Meta:
            model = models.Organization
            fields = '__all__'
            read_only_fields = Utils.read_only_fields + (
                'number_organizations',
                'number_course_meta',
                'number_categories',
                'number_users',
                'number_admins',
                'number_teachers',
                'number_students'
            )


class UserSerializers:
    class Person:
        class List(serializers.ModelSerializer):
            username = serializers.CharField(max_length=150, write_only=True)
            password = serializers.CharField(max_length=128, write_only=True)

            class Meta:
                model = models.Person
                exclude = ('id', )
                read_only_fields = Utils.read_only_fields + (
                    'user', 'last_login', 'ip'
                )

            def create(self, validated_data):
                u = validated_data.pop('username')
                p = validated_data.pop('password')

                user = User(username=u)
                user.set_password(p)
                user.save()
                validated_data['user'] = user

                return super().create(validated_data)

        class Instance(serializers.ModelSerializer):
            password = serializers.CharField(max_length=128, write_only=True, required=False)

            class Meta:
                model = models.Person
                exclude = ('id',)
                read_only_fields = Utils.read_only_fields + (
                    'user', 'last_login', 'ip'
                )

            def update(self, instance, validated_data):
                pwd = validated_data.pop('password', None)
                if pwd is not None:
                    instance.user.set_password(pwd)
                return super().update(instance, validated_data)

    class Login(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('username', 'password')
            extra_kwargs = {
                'username': {'write_only': True,
                             'validators': [RegexValidator()]},
                'password': {'write_only': True,
                             'style': {'input_type': 'password'}}
            }
