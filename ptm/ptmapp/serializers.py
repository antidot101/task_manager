from rest_framework import serializers
from .models import Task, TaskChangeHistory
from django.contrib.auth.models import User
from django.core import exceptions
import django.contrib.auth.password_validation as validators


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'user', 'task_name', 'description', 'creation_date', 'status', 'completion_date')
        read_only_fields = ['id', 'creation_date']
        extra_kwargs = {'completion_date': {'allow_null': True},
                        'user': {'write_only': True}}


class TaskChangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChangeHistory
        fields = '__all__'
        extra_kwargs = {'user': {'write_only': True}}


class UserRegisterSerializer(serializers.ModelSerializer):
    def validate(self, data):
        password = data.get('password')
        errors = dict()
        try:
            validators.validate_password(password=password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(UserRegisterSerializer, self).validate(data)


    class Meta:
        model = User
        fields = ('username', 'password')
