# Generated by Django 4.2.13 on 2024-07-16 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0031_sim_data_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sim',
            name='current_balance',
            field=models.CharField(blank=True, default=100000, max_length=10, null=True),
        ),
    ]