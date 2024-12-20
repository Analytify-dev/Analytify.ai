# Generated by Django 4.1.13 on 2024-06-18 16:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource_querysets',
            fields=[
                ('datasource_querysetid', models.AutoField(primary_key=True, serialize=False)),
                ('queryset_id', models.IntegerField()),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('server_id', models.IntegerField()),
                ('table_names', models.TextField()),
                ('filter_id_list', models.TextField()),
                ('is_custom_sql', models.BooleanField(default=False)),
                ('custom_query', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 425401))),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'datasource_querysets',
            },
        ),
        migrations.RenameField(
            model_name='datasourcefilter',
            old_name='datasource_filter_id',
            new_name='filter_id',
        ),
        migrations.RemoveField(
            model_name='chartfilters',
            name='alias',
        ),
        migrations.RemoveField(
            model_name='chartfilters',
            name='queryset_id',
        ),
        migrations.RemoveField(
            model_name='chartfilters',
            name='schema',
        ),
        migrations.RemoveField(
            model_name='chartfilters',
            name='table_name',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='alias',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='columns',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='custom_selected_data',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='datatype',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='filter_type',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='queryset_id',
        ),
        migrations.RemoveField(
            model_name='datasourcefilter',
            name='tables',
        ),
        migrations.AddField(
            model_name='chartfilters',
            name='row_data',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='datasourcefilter',
            name='col_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='datasourcefilter',
            name='data_type',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='datasourcefilter',
            name='filter_data',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='datasourcefilter',
            name='format_type',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='datasourcefilter',
            name='row_data',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 420399)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 20, 22, 15, 11, 420399)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 426396)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 430404)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 427397)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='user_id',
            field=models.IntegerField(db_column='user_id'),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 423398)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 427397)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 429400)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 425401)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 421398)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 424395)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 429400)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 18, 22, 15, 11, 418344)),
        ),
    ]
