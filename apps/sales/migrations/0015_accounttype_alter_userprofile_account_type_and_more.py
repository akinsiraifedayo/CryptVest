# Generated by Django 4.2.5 on 2024-05-28 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_admintransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('exact_name', models.CharField(max_length=50, unique=True)),
                ('price', models.DecimalField(decimal_places=2, default=99999, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='account_type',
            field=models.CharField(choices=[('retailer', 'Retailer'), ('vendor', 'Vendor')], default='retailer', max_length=8),
        ),
        migrations.CreateModel(
            name='AccountFunction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('account_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='functions', to='sales.accounttype')),
            ],
        ),
    ]
