# Generated by Django 4.2.13 on 2024-09-05 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0057_alter_userprofile_allowed_to_invest_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='wallet_balance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]