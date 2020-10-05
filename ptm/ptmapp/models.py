from django.db import models
from django.contrib.auth.models import User


statuses = [('New', 'New'), ('Planned', 'Planned'), ('In progress', 'In progress'), ('Completed', 'Completed')]


class Task(models.Model):
    task_name = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    status = models.CharField(max_length=20, choices=statuses, verbose_name="Статус", default='New')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")

    def __str__(self):
        return self.task_name

    class Meta:
        ordering = ['completion_date']


class TaskChangeHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание")
    status = models.CharField(max_length=20, choices=statuses, verbose_name="Статус", default='New')
    completion_date = models.DateTimeField(null=True, verbose_name="Дата завершения")
    changed_fields = models.CharField(max_length=100, verbose_name="Измененные поля")
    change_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")

    def __str__(self):
        return self.task_name

    class Meta:
        ordering = ['-change_date']