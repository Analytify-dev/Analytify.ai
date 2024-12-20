# Generated by Django 5.0.4 on 2024-05-13 12:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_queryset_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuerySets',
            fields=[
                ('queryset_id', models.AutoField(db_column='queryset_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('server_id', models.IntegerField()),
                ('table_names', models.TextField()),
                ('join_type', models.TextField()),
                ('joining_conditions', models.TextField()),
                ('is_custom_sql', models.BooleanField(default=False)),
                ('custom_query', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 178078))),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'querysets',
            },
        ),
        migrations.DeleteModel(
            name='QuerySet',
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 151395)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 15, 18, 18, 15, 151022)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 156051)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 153015)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 158049)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 13, 18, 18, 15, 140392)),
        ),
    ]
