# Generated by Django 4.2.13 on 2024-06-18 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0025_userprofile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlinetransaction',
            name='reference',
            field=models.CharField(max_length=101),
        ),
    ]