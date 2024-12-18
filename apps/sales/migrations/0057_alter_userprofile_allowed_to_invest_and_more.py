# Generated by Django 4.2.13 on 2024-09-04 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0056_delete_walletphrase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='allowed_to_invest',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
    ]
