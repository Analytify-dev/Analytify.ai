# Generated by Django 4.1.13 on 2024-09-09 05:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0077_userprofile_demo_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 677431)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 11, 11, 19, 38, 677431)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 681429)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 683431)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='dashboard_name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='file_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='queryset_id',
            field=models.TextField(blank=True, db_column='queryset_id', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='role_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='selected_sheet_ids',
            field=models.TextField(blank=True, db_column='selected_sheet_ids', null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='server_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='sheet_ids',
            field=models.TextField(blank=True, db_column='saved_sheet_ids', null=True),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='user_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 683431)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 681429)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 681429)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 679423)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 681429)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 682429)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 680429)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 678425)),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 678425)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 680429)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 682429)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 683431)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 11, 19, 38, 675433)),
        ),
    ]