# Generated by Django 5.1 on 2024-08-18 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0050_alter_sim_current_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sim',
            name='current_balance',
            field=models.IntegerField(default=400000),
        ),
    ]
