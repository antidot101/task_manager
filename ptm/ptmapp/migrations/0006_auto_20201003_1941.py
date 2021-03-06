# Generated by Django 2.2.1 on 2020-10-03 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ptmapp', '0005_auto_20201002_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Planned', 'Planned'), ('In progress', 'In progress'), ('Completed', 'Completed')], default='New', max_length=20, verbose_name='Статус'),
        ),
        migrations.CreateModel(
            name='TaskChangeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=150, verbose_name='Название')),
                ('description', models.TextField(max_length=1000, verbose_name='Описание')),
                ('status', models.CharField(choices=[('New', 'New'), ('Planned', 'Planned'), ('In progress', 'In progress'), ('Completed', 'Completed')], default='New', max_length=20, verbose_name='Статус')),
                ('completion_date', models.DateTimeField(null=True, verbose_name='Дата завершения')),
                ('change_fields', models.CharField(max_length=20, verbose_name='Измененные поля')),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ptmapp.Task')),
            ],
            options={
                'ordering': ['-change_date'],
            },
        ),
    ]
