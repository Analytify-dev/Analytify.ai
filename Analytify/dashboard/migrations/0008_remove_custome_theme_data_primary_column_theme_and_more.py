# Generated by Django 4.1.13 on 2024-12-13 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_custome_theme_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custome_theme_data',
            name='primary_column_theme',
        ),
        migrations.AddField(
            model_name='custome_theme_data',
            name='headertype',
            field=models.CharField(blank=True, db_column='headertype', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='custome_theme_data',
            name='menutype',
            field=models.CharField(blank=True, db_column='menutype', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='custome_theme_data',
            name='primary_colour_theme',
            field=models.CharField(blank=True, db_column='primary_colour_theme', max_length=500, null=True),
        ),
    ]
