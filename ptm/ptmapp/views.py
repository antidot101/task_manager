from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from .models import Task, TaskChangeHistory
from .serializers import TaskSerializer, TaskChangeHistorySerializer, UserRegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .utils import TaskFilter
from django.db.models import Q
from django.contrib.auth.hashers import make_password
import dateutil.parser as parser
from django.http import Http404


class WelcomeView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({"welcome": "Welcome to your Personal Task Manager. "
                                    "To get started with PTM please read the README "
                                    "https://github.com/antidot101/task_manager/blob/master/README.md"})


class TaskView(ListCreateAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = TaskFilter

    def get_queryset(self):
        queryset = Task.objects.filter(user_id=self.request.user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskUpdateView(RetrieveUpdateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            queryset = Task.objects.filter(user_id=self.request.user.id, pk=self.kwargs['pk'])
            if not queryset:
                raise Http404
            else:
                return queryset

    def update(self, request, *args, **kwargs):
        task_saved = get_object_or_404(Task.objects.filter(user_id=request.user.id),
                                       pk=self.kwargs['pk'])
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # detecting changed fields
        task_request = request.data
        editable_fields = ('task_name', 'description', 'status')
        changed_fields = ""
        for field in editable_fields:
            if getattr(task_saved, field) != task_request.get(field):
                changed_fields += field + ", "
        if task_request.get('completion_date') is not None:
            date_saved = task_saved.completion_date
            date_request = parser.parse(task_request['completion_date'])
            if date_saved != date_request:
                changed_fields += 'completion_date'
        changed_fields = changed_fields.strip(', ')
        if changed_fields == "":
            changed_fields = "No fields changed"

        # preparing data for task change history
        hist_data = serializer.data
        hist_data['task'] = self.kwargs['pk']
        hist_data['user'] = request.user.id
        hist_data['changed_fields'] = changed_fields
        hist_serializer = TaskChangeHistorySerializer(data=hist_data)
        hist_serializer.is_valid(raise_exception=True)
        hist_serializer.save()

        return Response(serializer.data)


class UserRegisterView(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get('username')
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = make_password(serializer.validated_data['password'])
        serializer.save(password=password)
        return Response({"success": "User '{}' created successfully".format(username)}, status=201)


class TaskChangeHistoryVeiw(ListAPIView):
    serializer_class = TaskChangeHistorySerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            queryset = TaskChangeHistory.objects.filter(Q(user_id=self.request.user.id) & Q(task_id=self.kwargs['pk']))
            return queryset
        queryset = TaskChangeHistory.objects.filter(user_id=self.request.user.id)
        return queryset
