# Generated by Django 4.2.13 on 2024-07-19 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0017_alter_investment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='reference',
            field=models.CharField(blank=True, max_length=101, null=True),
        ),
    ]