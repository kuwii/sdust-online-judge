# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import *


class Utils(object):
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
            read_only_fields = ('username', )

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
