# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import *


class Utils(object):
    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('User exists.')
        return value

    @staticmethod
    def validate_password(pwd):
        if pwd is None or pwd == '':
            raise serializers.ValidationError('Password can not be empty.')
        return pwd

    @staticmethod
    def validate_old_password(serializer, old_pwd):
        if old_pwd is not None:
            user = serializer.instance
            u = authenticate(username=user.username, password=old_pwd)
            if u is not None:
                if not user.is_active:
                    raise serializers.ValidationError('User disabled.')
            else:
                raise serializers.ValidationError('Password incorrect.')

            new_password = serializer.initial_data.get('new_password', None)
            if new_password is None or new_password == '':
                raise serializers.ValidationError('New password cannot be None.')

        return old_pwd

    @staticmethod
    def validate_sex(value):
        if value is not None and value not in UserProfile.SEX_CHOICES:
            raise serializers.ValidationError(
                'Sex can only be "MALE", "FEMALE" or "SECRET".'
            )
        return value


class PersonalSerializers(object):
    class LoginSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('username', 'password')
            extra_kwargs = {
                'username': {'write_only': True,
                             'validators': [RegexValidator()]},
                'password': {'write_only': True,
                             'style': {'input_type': 'password'}}
            }

    class PersonalInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserProfile
            exclude = ('user', 'is_staff', 'identities', 'courses')
            read_only_fields = (
                'username', 'creator', 'updater', 'create_time', 'update_time',
                'last_login', 'ip'
            )

    class UserPasswordSerializer(serializers.ModelSerializer):
        old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
        new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

        class Meta:
            model = User
            fields = ('username', 'old_password', 'new_password',)
            read_only_fields = ('username', )

        def validate_old_password(self, value):
            Utils.validate_old_password(self, value)
            return value

        @staticmethod
        def validate_new_password(value):
            return Utils.validate_password(value)

        def update(self, instance, validated_data):
            new_password = validated_data['new_password']
            instance.set_password(new_password)
            instance.save()
            return instance


class UserSerializers(object):
    class ListAdmin(serializers.ModelSerializer):
        password = serializers.CharField(max_length=128, write_only=True)
        identities = serializers.ListField(child=serializers.CharField(),
                                           source='get_identities',
                                           allow_null=True,
                                           allow_empty=True)

        @staticmethod
        def validate_username(value):
            return Utils.validate_username(value)

        @staticmethod
        def validate_password(value):
            return Utils.validate_password(value)

        @staticmethod
        def validate_sex(value):
            return Utils.validate_sex(value)

        @staticmethod
        def validate_identities(value):
            ret = {}
            for it in value:
                if it in SITE_IDENTITY_CHOICES:
                    ret[it] = True
            return ret

        class Meta:
            model = UserProfile
            exclude = ('user', 'courses')
            read_only_fields = (
                'creator', 'updater', 'create_time', 'update_time',
                'last_login', 'ip'
            )

        def create(self, validated_data):
            validated_data['identities'] = validated_data.pop('get_identities', {})
            profile = UserProfile.create_profile(**validated_data)
            profile.update_identities()
            return profile

    class InstanceAdmin(serializers.ModelSerializer):
        password = serializers.CharField(max_length=128, write_only=True)
        identities = serializers.ListField(child=serializers.CharField(),
                                           source='get_identities',
                                           allow_null=True,
                                           allow_empty=True)

        @staticmethod
        def validate_password(value):
            return Utils.validate_password(value)

        @staticmethod
        def validate_sex(value):
            return Utils.validate_sex(value)

        @staticmethod
        def validate_identities(value):
            ret = {}
            for it in value:
                if it in SITE_IDENTITY_CHOICES:
                    ret[it] = True
            return ret

        class Meta:
            model = UserProfile
            exclude = ('user', 'courses')
            read_only_fields = (
                'creator', 'updater', 'create_time', 'update_time',
                'last_login', 'ip'
            )

        def update(self, instance, validated_data):
            if 'password' in validated_data:
                instance.user.set_password(validated_data.pop('password'))
                instance.user.save()
            validated_data['identities'] = validated_data.pop('get_identities', {})
            ret = super().update(instance, validated_data)
            ret.update_identities()
            return instance
