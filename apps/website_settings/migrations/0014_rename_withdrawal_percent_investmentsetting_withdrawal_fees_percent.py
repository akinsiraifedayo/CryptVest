# Generated by Django 4.2.13 on 2024-09-07 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website_settings', '0013_investmentsetting_withdrawal_percent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investmentsetting',
            old_name='withdrawal_percent',
            new_name='withdrawal_fees_percent',
        ),
    ]
