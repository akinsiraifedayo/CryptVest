# Generated by Django 4.2.13 on 2024-06-18 09:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0002_investment_active_days_investment_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 6, 9, 41, 34, 519842, tzinfo=datetime.timezone.utc)),
        ),
    ]