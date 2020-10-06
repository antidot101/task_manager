from django_filters.rest_framework import FilterSet
import django_filters
from .models import Task


class TaskFilter(FilterSet):
    min_date = django_filters.IsoDateTimeFilter(field_name="completion_date", lookup_expr="gte")
    max_date = django_filters.IsoDateTimeFilter(field_name="completion_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ['id', 'status', 'completion_date']
