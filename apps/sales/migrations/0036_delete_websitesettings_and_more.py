# Generated by Django 4.2.13 on 2024-07-17 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0035_websitesettings_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WebsiteSettings',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='bonus_gotten_from_referrals',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]
