# Generated by Django 4.1.13 on 2025-02-07 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_alter_parent_ids_table_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasourcefilter',
            name='is_exclude',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
