from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListAPIView
from .models import Task, TaskChangeHistory
from .serializers import TaskSerializer, TaskChangeHistorySerializer, UserRegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .utils import TaskFilter
from django.db.models import Q
from django.contrib.auth.hashers import make_password
import dateutil.parser as parser


class WelcomeView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({"welcome": "Welcome to your Personal Task Manager. "
                                    "To get started with PTM please read the README "
                                    "https://github.com/antidot101/task_manager/blob/master/README.md"})


class TaskView(ListAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = TaskFilter

    def get_queryset(self):
        queryset = Task.objects.filter(user_id=self.request.user.id)
        return queryset

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def post(self, request):
        task = request.data
        task['user'] = request.user.id
        serializer = TaskSerializer(data=task)
        if serializer.is_valid(raise_exception=True):
            task_saved = serializer.save()
        return Response({"success": "Task '{}' created successfully".format(task_saved.task_name),
                         "created_task": serializer.data}, status=201)


class TaskUpdate(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            queryset = Task.objects.filter(Q(user_id=self.request.user.id) & Q(id=self.kwargs['pk']))
            return queryset

    def put(self, request, pk):
        saved_task = get_object_or_404(Task.objects.filter(user_id=request.user.id) , pk=pk)
        task = request.data
        serializer = TaskSerializer(instance=saved_task, data=task, partial=True)
        if serializer.is_valid(raise_exception=True):

            # detecting changed fields
            editable_fields = ('task_name', 'description', 'status')
            changed_fields = ""
            for field in editable_fields:
                if task.get(field) is not None:
                    if getattr(saved_task, field) != task.get(field):
                        changed_fields += field + ", "
            if task.get('completion_date') is not None:
                date_saved = saved_task.completion_date
                date_request = parser.parse(task['completion_date'])
                if date_saved != date_request:
                    changed_fields += 'completion_date'
            changed_fields = changed_fields.strip(', ')
            if changed_fields == "":
                changed_fields = "No fields changed"

            task_updated = serializer.save()

            # preparing data for task change history
            hist_data = task_updated.__dict__
            hist_data['task'] = pk
            hist_data['user'] = request.user.id
            hist_data['changed_fields'] = changed_fields
            serializer2 = TaskChangeHistorySerializer(data=hist_data)
            if serializer2.is_valid(raise_exception=True):
                serializer2.save()
        return Response({"success": "Task '{}' updated successfully".format(task_updated.task_name),
                         "updated_task": serializer.data})


class UserRegisterView(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response({"detail": "User '{}' already exist".format(username)})
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = make_password(serializer.validated_data['password'])
            User.objects.create_user(username=username, password=password)
        return Response({"success": "User '{}' created successfully".format(username)}, status=201)


class TaskChangeHistoryVeiw(ListAPIView):
    serializer_class = TaskChangeHistorySerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            queryset = TaskChangeHistory.objects.filter(Q(user_id=self.request.user.id) & Q(task_id=self.kwargs['pk']))
            return queryset
        queryset = TaskChangeHistory.objects.filter(user_id=self.request.user.id)
        return queryset
