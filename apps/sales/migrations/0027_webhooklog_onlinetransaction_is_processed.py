# Generated by Django 4.2.13 on 2024-06-18 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0026_alter_onlinetransaction_reference'),
    ]


    operations = [
        migrations.CreateModel(
            name='WebhookLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event_type', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_reference', models.CharField(blank=True, max_length=255, null=True)),
                ('payload', models.JSONField()),
                ('status', models.CharField(default='received', max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='onlinetransaction',
            name='is_processed',
            field=models.BooleanField(default=False),
        ),
    ]