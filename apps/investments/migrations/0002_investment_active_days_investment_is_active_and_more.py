# Generated by Django 4.2.13 on 2024-06-17 15:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='active_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='investment',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='investmenttype',
            name='roi_type',
            field=models.CharField(choices=[('daily', 'Daily'), ('monthly', 'Monthly')], default='monthly', max_length=8),
        ),
        migrations.AlterField(
            model_name='investment',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 5, 15, 16, 1, 459294, tzinfo=datetime.timezone.utc)),
        ),
    ]