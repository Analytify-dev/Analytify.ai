# Generated by Django 5.0.4 on 2024-05-16 06:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_chartfilters_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='functions_tb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_id', models.PositiveIntegerField(db_column='database_id')),
                ('function_ip', models.CharField(db_column='function', max_length=1500)),
                ('field_name', models.CharField(db_column='field_name', max_length=500)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 155204))),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'functions_table',
            },
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 139468)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 18, 12, 12, 33, 139468)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 155204)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 139468)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 155204)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 139468)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 139468)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 16, 12, 12, 33, 139468)),
        ),
    ]
