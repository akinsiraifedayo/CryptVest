# Generated by Django 4.2.13 on 2024-09-01 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_settings', '0010_alter_websitesettings_referral_withdrawal_allowed'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_investment', models.DecimalField(decimal_places=2, default=1000, max_digits=10)),
                ('max_investment', models.DecimalField(decimal_places=2, default=500000, max_digits=10)),
                ('min_withdrawal', models.DecimalField(decimal_places=2, default=1000, max_digits=10)),
                ('max_withdrawal', models.DecimalField(decimal_places=2, default=500000, max_digits=10)),
            ],
        ),
    ]
