# Generated by Django 4.1.13 on 2024-10-03 12:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0050_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 3, 18, 18, 10, 920623)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 3, 19, 18, 10, 920623)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 3, 18, 18, 10, 920623)),
        ),
    ]
