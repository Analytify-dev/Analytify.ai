# Generated by Django 4.1.13 on 2024-08-08 12:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0063_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='grid_type',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('grid_type', models.CharField(db_column='grid_type', max_length=100)),
            ],
            options={
                'db_table': 'grid_type',
            },
        ),
        migrations.AddField(
            model_name='dashboard_data',
            name='grid_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dashboard_data',
            name='height',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dashboard_data',
            name='selected_sheet_ids',
            field=models.CharField(blank=True, db_column='selected_sheet_ids', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='dashboard_data',
            name='width',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 891155)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 10, 17, 45, 19, 891155)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 895153)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 897153)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='sheet_ids',
            field=models.CharField(blank=True, db_column='saved_sheet_ids', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 898153)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 894153)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 895153)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 893153)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 895153)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 896153)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 894153)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 891155)),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 892154)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 893153)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 896153)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 898153)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 889154)),
        ),
    ]