# Generated by Django 4.1.13 on 2024-07-23 15:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0042_previlages_role_created_at_role_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 626444)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 25, 20, 42, 20, 626444)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 630429)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 632428)),
        ),
        migrations.AlterField(
            model_name='dashboardfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 632428)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 629428)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 630429)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 628445)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 630429)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 631433)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 629428)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 627433)),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 627433)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 629428)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 631433)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 632428)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 23, 20, 42, 20, 625448)),
        ),
        migrations.AlterModelTable(
            name='previlages',
            table='previlages',
        ),
    ]
