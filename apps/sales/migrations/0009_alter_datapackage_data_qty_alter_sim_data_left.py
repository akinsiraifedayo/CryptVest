# Generated by Django 4.2.13 on 2024-05-23 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_transaction_package_transaction_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapackage',
            name='data_qty',
            field=models.IntegerField(max_length=50),
        ),
        migrations.AlterField(
            model_name='sim',
            name='data_left',
            field=models.IntegerField(blank=True, default=5000, null=True),
        ),
    ]
