# Generated by Django 5.1 on 2024-08-18 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0051_alter_sim_current_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='sim',
            name='just_refreshed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]