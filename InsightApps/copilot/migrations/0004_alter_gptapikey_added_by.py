# Generated by Django 4.1.13 on 2024-09-11 13:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('copilot', '0003_alter_gptapikey_added_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gptapikey',
            name='added_by',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
