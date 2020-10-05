from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Task, TaskChangeHistory
from .serializers import TaskSerializer, TaskChangeHistorySerializer, UserRegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.hashers import make_password
import dateutil.parser as parser


class TaskFilter(FilterSet):
    min_date = django_filters.IsoDateTimeFilter(field_name="completion_date", lookup_expr="gte")
    max_date = django_filters.IsoDateTimeFilter(field_name="completion_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ['id', 'status', 'completion_date']


class TaskView(ListAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = TaskFilter

    def get_queryset(self):
        token_obj = Token.objects.get(key=self.request.auth)
        queryset = Task.objects.filter(user_id=token_obj.user_id)
        return queryset

    def post(self, request):
        token_obj = Token.objects.get(key=self.request.auth)
        if not request.data.get('task'):
            return Response({"detail": "Object key 'task' expected"})
        task = request.data['task']
        task['user'] = token_obj.user_id
        serializer = TaskSerializer(data=task)
        if serializer.is_valid(raise_exception=True):
            if task.get('completion_date') is not None:
                if parser.parse(task['completion_date'], ignoretz=True) <= datetime.now():
                    return Response({"detail": "Incorrect completion_date"})
            task_saved = serializer.save()
        return Response({"success": "Task '{}' created successfully".format(task_saved.task_name)}, status=201)


class TaskUpdate(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        token_obj = Token.objects.get(key=self.request.auth)
        if 'pk' in self.kwargs:
            queryset = Task.objects.filter(Q(user_id=token_obj.user_id) & Q(id=self.kwargs['pk']))
            return queryset

    def put(self, request, pk):
        token_obj = Token.objects.get(key=self.request.auth)
        saved_task = get_object_or_404(Task.objects.filter(user_id=token_obj.user_id) , pk=pk)
        data = request.data.get('task')
        serializer = TaskSerializer(instance=saved_task, data=data, partial=True)
        editable_fields = ('task_name', 'description', 'status')
        changed_fields = ""
        if serializer.is_valid(raise_exception=True):
            # detecting changed fields
            for field in editable_fields:
                print(getattr(saved_task, field))
                if getattr(saved_task, field) != data.get(field):
                    changed_fields += field + ", "
            # checking completion_date correctness
            if data.get('completion_date') is not None:
                if parser.parse(data['completion_date'], ignoretz=True) <= datetime.now():
                    return Response({"detail": "Incorrect completion_date"})
                date_saved = saved_task.completion_date.isoformat()
                date_request = parser.parse(data['completion_date']).isoformat()
                if date_saved != date_request:
                    changed_fields += 'completion_date'
            changed_fields = changed_fields.strip(', ')
            if changed_fields == "":
                changed_fields = "No fields changed"

            task_saved = serializer.save()
            data['task'] = pk
            data['user'] = token_obj.user_id
            data['changed_fields'] = changed_fields
            serializer2 = TaskChangeHistorySerializer(data=data, partial=True)
            if serializer2.is_valid(raise_exception=True):
                serializer2.save()
        return Response({"success": "Task '{}' updated successfully".format(task_saved.task_name)})


class UserRegisterView(ObtainAuthToken):
    def post(self, request):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response({"detail": "User '{}' already exist".format(username)})
        password = make_password(request.data.get('password'))
        data = {}
        data['username'], data['password'] = username, password
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
        return Response({"success": "User '{}' created successfully".format(user_saved.username)}, status=201)


class TaskChangeHistoryVeiw(ListAPIView):
    serializer_class = TaskChangeHistorySerializer

    def get_queryset(self):
        token_obj = Token.objects.get(key=self.request.auth)
        if 'pk' in self.kwargs:
            queryset = TaskChangeHistory.objects.filter(Q(user_id=token_obj.user_id) & Q(task_id=self.kwargs['pk']))
            return queryset
        queryset = TaskChangeHistory.objects.filter(user_id=token_obj.user_id)
        return queryset
