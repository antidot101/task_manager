from django.contrib import admin
from .models import Task, TaskChangeHistory


admin.site.register(Task)
admin.site.register(TaskChangeHistory)
