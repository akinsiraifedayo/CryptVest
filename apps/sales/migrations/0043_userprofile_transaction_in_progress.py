# Generated by Django 4.2.13 on 2024-08-04 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0042_sim_priority_sim_sales_sim_data_le_f9d648_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='transaction_in_progress',
            field=models.BooleanField(default=False),
        ),
    ]