# Generated by Django 4.1.13 on 2024-10-16 14:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0056_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 16, 19, 31, 2, 803073)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 16, 20, 31, 2, 803073)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 16, 19, 31, 2, 804071)),
        ),
    ]