from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.authtoken.models import Token
from .models import Task, TaskChangeHistory
from .serializers import TaskSerializer, TaskChangeHistorySerializer, UserRegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .utils import TaskFilter
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.hashers import make_password
import dateutil.parser as parser


class WelcomeView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({"welcome": "Welcome to your Personal Task Manager. To get started with PTM please read the README "
                                    "https://github.com/antidot101/task_manager/blob/master/README.md"})


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
                if data.get(field) is not None:
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
            hist_data = task_saved.__dict__
            hist_data['task'] = pk
            hist_data['user'] = token_obj.user_id
            hist_data['changed_fields'] = changed_fields
            serializer2 = TaskChangeHistorySerializer(data=hist_data)
            if serializer2.is_valid(raise_exception=True):
                serializer2.save()
        return Response({"success": "Task '{}' updated successfully".format(task_saved.task_name)})


class UserRegisterView(APIView):
    permission_classes = ()

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
