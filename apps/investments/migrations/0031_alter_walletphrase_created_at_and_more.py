# Generated by Django 4.2.13 on 2024-09-02 09:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0030_alter_walletphrase_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='walletphrase',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='walletphrase',
            name='expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]