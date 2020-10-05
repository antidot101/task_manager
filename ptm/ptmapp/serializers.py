from rest_framework import serializers
from .models import Task, TaskChangeHistory
from django.contrib.auth.models import User


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'user', 'task_name', 'description', 'creation_date', 'status', 'completion_date')
        read_only_fields = ['id', 'creation_date']
        extra_kwargs = {'completion_date': {'allow_null': True},
                        'user': {'write_only': True}}


    # task_name = serializers.CharField(max_length=150)
    # description = serializers.CharField()
    # creation_date = serializers.DateTimeField(read_only=True)
    # status = serializers.IntegerField()
    # completion_date = serializers.DateTimeField(allow_null=True)
    #
    # def create(self, validated_data):
    #     return Task.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     instance.task_name = validated_data.get('task_name', instance.task_name)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.completion_date = validated_data.get('completion_date', instance.completion_date)
    #     # instance.author_id = validated_data.get('author_id', instance.author_id)
    #     instance.save()
    #     return instance

class TaskChangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChangeHistory
        fields = '__all__'
        # exclude = ['task', 'user']
        extra_kwargs = {'user': {'write_only': True}}


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
