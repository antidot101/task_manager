from django.urls import path
from .views import TaskView, TaskUpdate, UserRegisterView, TaskChangeHistoryVeiw, WelcomeView
from rest_framework.authtoken import views


urlpatterns = [
    path('', WelcomeView.as_view()),
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('tasks/<int:pk>', TaskUpdate.as_view(), name='task_update'),
    path('tasks/change-history/', TaskChangeHistoryVeiw.as_view(), name='all_tasks_history'),
    path('tasks/change-history/<int:pk>', TaskChangeHistoryVeiw.as_view(), names='task_history'),
    path('register/', UserRegisterView.as_view(), name='registration'),
    path('token-auth/', views.obtain_auth_token, name='get_token')
]