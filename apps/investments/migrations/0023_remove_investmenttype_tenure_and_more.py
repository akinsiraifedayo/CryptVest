# Generated by Django 5.1 on 2024-08-23 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0022_alter_roitransaction_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investmenttype',
            name='tenure',
        ),
        migrations.AddField(
            model_name='investmenttype',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
    ]