# Generated by Django 2.2.1 on 2020-10-03 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ptmapp', '0007_auto_20201003_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskchangehistory',
            name='changed_fields',
            field=models.CharField(max_length=100, verbose_name='Измененные поля'),
        ),
    ]
