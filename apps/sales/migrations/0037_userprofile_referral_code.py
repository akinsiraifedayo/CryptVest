# Generated by Django 4.2.13 on 2024-07-17 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0036_delete_websitesettings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='referral_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]