# Generated by Django 4.2.13 on 2024-09-07 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0059_userprofile_fees_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='withdrawal_fees_percent',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
