# Generated by Django 5.1 on 2024-08-16 22:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0048_sim_confirmed_logged_in'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sim',
            options={'ordering': ['-expiry_date']},
        ),
        migrations.AddField(
            model_name='sim',
            name='expiry_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 12, 31, 23, 59, 59), null=True),
        ),
        migrations.AddIndex(
            model_name='sim',
            index=models.Index(fields=['expiry_date'], name='sales_sim_expiry__1d10ca_idx'),
        ),
    ]