from django.urls import path
from .views import TaskView, TaskUpdate, UserRegisterView, TaskChangeHistoryVeiw
from rest_framework.authtoken import views


urlpatterns = [
    path('tasks/', TaskView.as_view()),
    path('tasks/<int:pk>', TaskUpdate.as_view()),
    path('tasks/change-history/', TaskChangeHistoryVeiw.as_view()),
    path('tasks/change-history/<int:pk>', TaskChangeHistoryVeiw.as_view()),
    path('register/', UserRegisterView.as_view()),
    path('token-auth/', views.obtain_auth_token) # ObtainAuthTokenView.as_view()
]