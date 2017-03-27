from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from . import models


class Utils(object):
    read_only_fields = ('creator', 'create_time', 'updater', 'update_time')

    @staticmethod
    def create_user_profile(**kwargs):
        creator = kwargs.get('creator', None)
        updater = kwargs.get('updater', None)

        # 创建用户
        username = kwargs['username']
        password = kwargs['password']
        active = kwargs.get('available', True)

        user = models.User(username=username, is_active=active)
        user.set_password(password)
        user.save()

        # 创建用户信息
        name = kwargs.get('name', None)
        sex = kwargs.get('sex', 'SECRET')
        phone = kwargs.get('phone', None)
        email = kwargs.get('email', None)
        github = kwargs.get('github', None)
        qq = kwargs.get('qq', None)
        weixin = kwargs.get('weixin', None)
        blog = kwargs.get('blog', None)
        introduction = kwargs.get('introduction', None)

        profile = models.UserProfile(user=user, username=username,
                                     name=name, sex=sex,
                                     phone=phone, email=email, github=github, qq=qq, weixin=weixin, blog=blog,
                                     introduction=introduction,
                                     is_staff=False,
                                     creator=creator, updater=updater)
        profile.save()

        return user, profile


class OrgSerializers(object):
    """
    与机构管理相关的Serializer。
    """
    class Organization(object):
        class ListAdmin(serializers.ModelSerializer):
            @staticmethod
            def validate_parent(value):
                root = models.Organization.objects.get(name='ROOT')

                checked = set()
                cur = value

                while cur is not None and cur.id not in checked:
                    if cur.id == root.id:
                        return value
                    checked.add(cur.id)
                    cur = cur.parent

                raise serializers.ValidationError('Organization unreachable.')

            class Meta:
                model = models.Organization
                fields = '__all__'
                read_only_fields = Utils.read_only_fields + (
                    'number_organizations', 'number_students', 'number_teachers', 'number_admins'
                )
                extra_kwargs = {
                    'parent': {'allow_null': False, 'required': True}
                }

        class InstanceAdmin(serializers.ModelSerializer):
            def validate_parent(self, value):
                root = models.Organization.objects.get(name='ROOT')

                checked = set()
                cur = value
                checked.add(self.instance.id)

                while cur is not None and cur.id not in checked:
                    if cur.id == root.id:
                        return value
                    checked.add(cur.id)
                    cur = cur.parent

                raise serializers.ValidationError('Organization unreachable.')

            class Meta:
                model = models.Organization
                fields = '__all__'
                read_only_fields = Utils.read_only_fields + (
                    'number_organizations', 'number_students', 'number_teachers', 'number_admins'
                )
                extra_kwargs = {
                    'parent': {'allow_null': False, 'required': True}
                }

    class EduAdmin(object):
        class ListAdmin(serializers.ModelSerializer):
            username = serializers.CharField(max_length=150, write_only=True)
            password = serializers.CharField(max_length=128, write_only=True)

            class Meta:
                model = models.EduAdmin
                exclude = ('organization', 'user', 'profile')
                read_only_fields = Utils.read_only_fields

            def create(self, validated_data):
                u = validated_data.get('username')
                p = validated_data.pop('password')
                active = validated_data.get('available', False)
                name = validated_data.get('name', None)
                sex = validated_data.get('sex', 'SECRET')
                phone = validated_data.get('phone', None)
                email = validated_data.get('email', None)
                creator = validated_data.get('creator', None)
                updater = validated_data.get('updater', None)

                user, profile = Utils.create_user_profile(
                    username=u, password=p, available=active,
                    name=name, sex=sex, phone=phone, email=email,
                    creator=creator, updater=updater
                )

                organization = validated_data.get('organization')
                profile.identities = {models.IdentityChoices.edu_admin: [organization.id]}
                profile.save()

                edu_admin = models.EduAdmin(user=user, profile=profile, organization=organization,
                                            name=name, sex=sex, phone=phone, email=email,
                                            creator=creator, updater=updater)
                edu_admin.save()
                return edu_admin


class UserSerializers(object):
    """
    与用户管理相关的Serializer。
    """
    class Utils(object):
        """
        用于验证用户参数合法性的方法的集合。
        """
        @staticmethod
        def validate_username(value):
            """
            验证是否已存在相同用户名的用户。
            :param value: 用户名，传入前必已通过DRF合法性验证。
            :return: 传入的value。
            """
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError('User exists.')
            return value

        @staticmethod
        def validate_password(value):
            """
            用于验证传入的密码是否不为空。
            :param value: 密码，传入前必已通过DRF默认的合法性检查。
            :return:传入的value。
            """
            if value is None or value == '':
                raise serializers.ValidationError('Password can not be empty.')
            return value

        @staticmethod
        def validate_old_password(serializer, instance, value):
            """
            修改密码时检查旧密码是否正确以及新密码是否不为空。
            :param serializer: 需要修改用户信息的Serializer。
            :param instance: 需要修改的用户实例。
            :param value: 旧密码。
            :return: 传入的value本身。
            """
            if value is not None:
                user = instance.user
                u = authenticate(username=instance.username, password=value)
                if u is not None:
                    if not user.is_active:
                        raise serializers.ValidationError('User disabled.')
                else:
                    raise serializers.ValidationError('Password incorrect.')

                new_password = serializer.initial_data.get('new_password', None)
                if new_password is None or new_password == '':
                    raise serializers.ValidationError('New password cannot be None.')

            return value

        @staticmethod
        def validate_sex(value):
            """
            验证性别值是否合法。
            规则：
                性别仅可为"male"，"female"或"secret"。
            :param value: 性别值，字符串。
            :return: 传入的value。
            """
            if value is not None and value not in models.UserProfile.SEX_CHOICES:
                raise serializers.ValidationError(
                    'Sex can only be "MALE", "FEMALE" or "SECRET".'
                )
            return value

    class Admin(object):
        """
        网站管理员的Serializer。
        """
        class ListAdmin(serializers.ModelSerializer):
            password = serializers.CharField(max_length=128, write_only=True)
            identities = serializers.ListField(child=serializers.CharField(),
                                               source='get_site_identities',
                                               allow_null=True,
                                               allow_empty=True)

            @staticmethod
            def validate_username(value):
                return UserSerializers.Utils.validate_username(value)

            @staticmethod
            def validate_password(value):
                return UserSerializers.Utils.validate_password(value)

            @staticmethod
            def validate_sex(value):
                return UserSerializers.Utils.validate_sex(value)

            @staticmethod
            def validate_identities(value):
                for it in value:
                    if it == models.IdentityChoices.root:
                        raise serializers.ValidationError('You have no permission to create root')
                    if it == models.IdentityChoices.user_admin:
                        raise serializers.ValidationError('You have no permission to create user administrator')
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', 'is_staff', )
                read_only_fields = Utils.read_only_fields + (
                    'last_login', 'ip',
                )

            def create(self, validated_data):
                u = validated_data.get('username')
                p = validated_data.pop('password')
                active = validated_data.get('available', False)
                identities = validated_data.pop('get_site_identities', [])

                id_ret = dict()
                for id_str in identities:
                    if id_str in models.SITE_IDENTITY_CHOICES:
                        id_ret[id_str] = True
                validated_data['identities'] = id_ret
                validated_data['is_staff'] = True

                user = User(username=u)
                user.set_password(p)
                user.is_active = active
                user.save()
                validated_data['user'] = user

                return super().create(validated_data)

        class ListRoot(ListAdmin):
            def __init__(self, instance=None, data=serializers.empty, **kwargs):
                super().__init__(instance=instance, data=data, **kwargs)

            @staticmethod
            def validate_identities(value):
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', 'is_staff', )
                read_only_fields = Utils.read_only_fields + (
                    'last_login', 'ip',
                )

        class InstanceAdmin(serializers.ModelSerializer):
            password = serializers.CharField(max_length=128, write_only=True)
            identities = serializers.ListField(child=serializers.CharField(),
                                               source='get_site_identities',
                                               allow_null=True,
                                               allow_empty=True)

            @staticmethod
            def validate_password(value):
                return UserSerializers.Utils.validate_password(value)

            @staticmethod
            def validate_sex(value):
                return UserSerializers.Utils.validate_sex(value)

            def validate_identities(self, value):
                instance = self.instance
                if models.IdentityChoices.root in instance.identities \
                        or models.IdentityChoices.user_admin in instance.identities:
                    raise serializers.ValidationError(
                        'You have no permission to change identity or root or user administrator'
                    )
                for it in value:
                    if it == models.IdentityChoices.root:
                        raise serializers.ValidationError('You have no permission to promote a user to root')
                    if it == models.IdentityChoices.user_admin:
                        raise serializers.ValidationError('You have no permission to '
                                                          'promote a user to user administrator')
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', 'is_staff', )
                read_only_fields = Utils.read_only_fields + (
                    'username', 'last_login', 'ip'
                )

            def update(self, instance, validated_data):
                pwd = validated_data.pop('password', None)
                if pwd is not None:
                    instance.user.set_password(pwd)
                active = validated_data.pop('available', None)
                if active is not None:
                    instance.user.is_active = active
                instance.user.save()

                identities = validated_data.pop('get_site_identities', False)
                if identities is not False:
                    id_ret = {}
                    # 处理全局身份
                    if identities is None:
                        identities = []
                    for id_str in identities:
                        if id_str in models.SITE_IDENTITY_CHOICES:
                            id_ret[id_str] = True
                    # 处理机构相关身份
                    former_identities = instance.identities
                    if models.Student.IDENTITY_WORD in former_identities:
                        id_ret[models.Student.IDENTITY_WORD] = former_identities[models.Student.IDENTITY_WORD]
                    if models.Teacher.IDENTITY_WORD in former_identities:
                        id_ret[models.Teacher.IDENTITY_WORD] = former_identities[models.Teacher.IDENTITY_WORD]
                    if models.EduAdmin.IDENTITY_WORD in former_identities:
                        id_ret[models.EduAdmin.IDENTITY_WORD] = former_identities[models.EduAdmin.IDENTITY_WORD]
                    validated_data['identities'] = id_ret

                return super().update(instance, validated_data)

        class InstanceRoot(InstanceAdmin):
            def __init__(self, instance=None, data=serializers.empty, **kwargs):
                super().__init__(instance=instance, data=data, **kwargs)

            def validate_identities(self, value):
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', )
                read_only_fields = Utils.read_only_fields + (
                    'username', 'last_login', 'ip'
                )

    class User(object):
        """
        用户的相关serializer。
        """
        class ListAdmin(serializers.ModelSerializer):
            password = serializers.CharField(max_length=128, write_only=True)
            identities = serializers.ListField(child=serializers.CharField(),
                                               source='get_site_identities',
                                               allow_null=True,
                                               allow_empty=True)

            @staticmethod
            def validate_username(value):
                return UserSerializers.Utils.validate_username(value)

            @staticmethod
            def validate_password(value):
                return UserSerializers.Utils.validate_password(value)

            @staticmethod
            def validate_sex(value):
                return UserSerializers.Utils.validate_sex(value)

            @staticmethod
            def validate_identities(value):
                for it in value:
                    if it == models.IdentityChoices.root:
                        raise serializers.ValidationError('You have no permission to create root')
                    if it == models.IdentityChoices.user_admin:
                        raise serializers.ValidationError('You have no permission to create user administrator')
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', )
                read_only_fields = Utils.read_only_fields + (
                    'last_login', 'ip',
                )

            def create(self, validated_data):
                u = validated_data.get('username')
                p = validated_data.pop('password')
                active = validated_data.get('available', False)
                identities = validated_data.pop('get_site_identities', [])

                id_ret = dict()
                for id_str in identities:
                    if id_str in models.SITE_IDENTITY_CHOICES:
                        id_ret[id_str] = True
                validated_data['identities'] = id_ret
                validated_data['is_staff'] = True

                user = User(username=u)
                user.set_password(p)
                user.is_active = active
                user.save()
                validated_data['user'] = user

                return super().create(validated_data)

        class ListRoot(ListAdmin):
            def __init__(self, instance=None, data=serializers.empty, **kwargs):
                super().__init__(instance=instance, data=data, **kwargs)

            @staticmethod
            def validate_identities(value):
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user',)
                read_only_fields = Utils.read_only_fields + (
                    'last_login', 'ip',
                )

        class InstanceAdmin(serializers.ModelSerializer):
            password = serializers.CharField(max_length=128, write_only=True)
            identities = serializers.ListField(child=serializers.CharField(),
                                               source='get_site_identities',
                                               allow_null=True,
                                               allow_empty=True)

            @staticmethod
            def validate_password(value):
                return UserSerializers.Utils.validate_password(value)

            @staticmethod
            def validate_sex(value):
                return UserSerializers.Utils.validate_sex(value)

            def validate_identities(self, value):
                instance = self.instance
                if models.IdentityChoices.root in instance.identities \
                        or models.IdentityChoices.user_admin in instance.identities:
                    raise serializers.ValidationError(
                        'You have no permission to change identity or root or user administrator'
                    )
                for it in value:
                    if it == models.IdentityChoices.root:
                        raise serializers.ValidationError('You have no permission to promote a user to root')
                    if it == models.IdentityChoices.user_admin:
                        raise serializers.ValidationError('You have no permission to '
                                                          'promote a user to user administrator')
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', 'is_staff', )
                read_only_fields = Utils.read_only_fields + (
                    'username', 'last_login', 'ip'
                )

            def update(self, instance, validated_data):
                pwd = validated_data.pop('password', None)
                if pwd is not None:
                    instance.user.set_password(pwd)
                active = validated_data.pop('available', None)
                if active is not None:
                    instance.user.is_active = active
                instance.user.save()

                identities = validated_data.pop('get_site_identities', False)
                if identities is not False:
                    id_ret = {}
                    # 处理全局身份
                    if identities is None:
                        identities = []
                    for id_str in identities:
                        if id_str in models.SITE_IDENTITY_CHOICES:
                            id_ret[id_str] = True
                    # 处理机构相关身份
                    former_identities = instance.identities
                    if models.Student.IDENTITY_WORD in former_identities:
                        id_ret[models.Student.IDENTITY_WORD] = former_identities[models.Student.IDENTITY_WORD]
                    if models.Teacher.IDENTITY_WORD in former_identities:
                        id_ret[models.Teacher.IDENTITY_WORD] = former_identities[models.Teacher.IDENTITY_WORD]
                    if models.EduAdmin.IDENTITY_WORD in former_identities:
                        id_ret[models.EduAdmin.IDENTITY_WORD] = former_identities[models.EduAdmin.IDENTITY_WORD]
                    validated_data['identities'] = id_ret

                return super().update(instance, validated_data)

        class InstanceRoot(InstanceAdmin):
            def __init__(self, instance=None, data=serializers.empty, **kwargs):
                super().__init__(instance=instance, data=data, **kwargs)

            def validate_identities(self, value):
                return value

            class Meta:
                model = models.UserProfile
                exclude = ('user', )
                read_only_fields = Utils.read_only_fields + (
                    'username', 'last_login', 'ip'
                )

    class Self(object):
        """
        用户对自己操作的相关Serializer。
        """
        class Instance(serializers.ModelSerializer):
            old_password = serializers.CharField(max_length=128, write_only=True, required=False)
            new_password = serializers.CharField(max_length=128, write_only=True, required=False)

            class Meta:
                model = models.UserProfile
                exclude = ('user', )
                read_only_fields = Utils.read_only_fields + (
                    'username', 'last_login', 'ip',
                    'org_identities', 'identities'
                )

            @staticmethod
            def validate_sex(value):
                return UserSerializers.Utils.validate_sex(value)

            def validate_old_password(self, value):
                return UserSerializers.Utils.validate_old_password(self, self.instance, value)

            @staticmethod
            def validate_new_password(value):
                if value is None or value == '':
                    raise serializers.ValidationError('Password can not be empty')
                return value

            def update(self, instance, validated_data):
                old_pwd = validated_data.pop('old_password', None)
                new_pwd = validated_data.pop('new_password', None)
                user = instance.user
                if old_pwd is not None:
                    user.set_password(new_pwd)
                    user.save()
                validated_data['updater'] = user.username
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
