# Generated by Django 4.2.13 on 2024-09-01 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0024_investmenttype_tenure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investmenttype',
            name='tenure',
        ),
    ]
