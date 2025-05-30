# Generated by Django 4.1.13 on 2024-12-06 07:32

import dashboard.models
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_Activation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.IntegerField(db_column='user_id', null=True)),
                ('email', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('key', models.CharField(blank=True, max_length=100, null=True)),
                ('otp', models.PositiveIntegerField()),
                ('expiry_date', models.DateTimeField(default=dashboard.models.get_expiry_date)),
            ],
            options={
                'db_table': 'account_activation',
            },
        ),
        migrations.CreateModel(
            name='calculation_field',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('queryset_id', models.IntegerField(blank=True, null=True)),
                ('server_id', models.IntegerField(blank=True, null=True)),
                ('file_id', models.IntegerField(blank=True, null=True)),
                ('field_name', models.CharField(blank=True, max_length=500, null=True)),
                ('nestedFunctionName', models.CharField(blank=True, max_length=500, null=True)),
                ('functionName', models.CharField(blank=True, max_length=500, null=True)),
                ('cal_logic', models.TextField(blank=True, db_column='calculation_logic', null=True)),
                ('actual_dragged_logic', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'calculation_field',
            },
        ),
        migrations.CreateModel(
            name='ChartFilters',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('filter_id', models.AutoField(db_column='filter_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('hierarchy_id', models.IntegerField()),
                ('datasource_querysetid', models.IntegerField(blank=True, null=True)),
                ('queryset_id', models.IntegerField(blank=True, null=True)),
                ('col_name', models.CharField(max_length=500)),
                ('data_type', models.CharField(max_length=500)),
                ('filter_data', models.TextField(null=True)),
                ('row_data', models.TextField(null=True)),
                ('format_type', models.CharField(max_length=500, null=True)),
                ('is_exclude', models.BooleanField(default=False, null=True)),
                ('field_logic', models.TextField(blank=True, default=None, null=True)),
                ('is_calculated', models.BooleanField(default=False, null=True)),
            ],
            options={
                'db_table': 'chart_filters',
            },
        ),
        migrations.CreateModel(
            name='charts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chart_type', models.CharField(max_length=500, null=True)),
                ('min_measures', models.CharField(max_length=500, null=True)),
                ('max_measures', models.CharField(max_length=500, null=True)),
                ('min_dimensions', models.CharField(max_length=500, null=True)),
                ('max_dimensions', models.CharField(max_length=500, null=True)),
                ('min_dates', models.CharField(max_length=500, null=True)),
                ('max_dates', models.CharField(max_length=500, null=True)),
                ('min_geo', models.CharField(max_length=500, null=True)),
                ('max_geo', models.CharField(max_length=500, null=True)),
            ],
            options={
                'db_table': 'charts',
            },
        ),
        migrations.CreateModel(
            name='dashboard_data',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(db_column='dashboard_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('server_id', models.TextField(blank=True, null=True)),
                ('queryset_id', models.TextField(blank=True, db_column='queryset_id', default=None, null=True)),
                ('file_id', models.TextField(blank=True, null=True)),
                ('is_sample', models.BooleanField(default=False)),
                ('sheet_ids', models.TextField(blank=True, db_column='saved_sheet_ids', null=True)),
                ('selected_sheet_ids', models.TextField(blank=True, db_column='selected_sheet_ids', null=True)),
                ('height', models.CharField(blank=True, max_length=100, null=True)),
                ('width', models.CharField(blank=True, max_length=100, null=True)),
                ('grid_id', models.IntegerField(blank=True, null=True)),
                ('role_ids', models.TextField(blank=True, null=True)),
                ('user_ids', models.TextField(blank=True, null=True)),
                ('dashboard_name', models.CharField(blank=True, max_length=1000, null=True)),
                ('datapath', models.FileField(blank=True, db_column='dashboard_data_path', max_length=1000, null=True, upload_to='insightapps/dashboard/')),
                ('datasrc', models.CharField(blank=True, db_column='dashboard_data_source', max_length=1000, null=True)),
                ('imagepath', models.ImageField(blank=True, db_column='dashboard_image_path', max_length=1000, null=True, upload_to='insightapps/dashboard/images/')),
                ('imagesrc', models.CharField(blank=True, db_column='dashboard_image_source', max_length=1000, null=True)),
                ('dashboard_tag_name', models.CharField(blank=True, db_column='dashboard_tag_name', max_length=1000, null=True)),
                ('is_public', models.BooleanField(db_column='is_public', default=False)),
            ],
            options={
                'db_table': 'dashboard_data',
            },
        ),
        migrations.CreateModel(
            name='Dashboard_drill_through',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('action_name', models.CharField(blank=True, max_length=500, null=True)),
                ('queryset_id', models.IntegerField(blank=True, null=True)),
                ('dashboard_id', models.IntegerField(blank=True, null=True)),
                ('source_sheet_id', models.IntegerField(blank=True, db_column='source_sheet_id', null=True)),
                ('target_sheet_id', models.TextField(blank=True, db_column='target_sheet_id', null=True)),
            ],
            options={
                'db_table': 'dashboard_drill_through_data',
            },
        ),
        migrations.CreateModel(
            name='DashboardFilters',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('dashboard_id', models.IntegerField(blank=True, null=True)),
                ('sheet_id_list', models.CharField(blank=True, max_length=200, null=True)),
                ('filter_name', models.CharField(max_length=200, null=True)),
                ('table_name', models.CharField(max_length=200, null=True)),
                ('column_name', models.CharField(max_length=200, null=True)),
                ('column_datatype', models.CharField(max_length=200, null=True)),
                ('queryset_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'dashboard_filters',
            },
        ),
        migrations.CreateModel(
            name='DataSource_querysets',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('datasource_querysetid', models.AutoField(primary_key=True, serialize=False)),
                ('queryset_id', models.IntegerField()),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('hierarchy_id', models.IntegerField()),
                ('table_names', models.TextField()),
                ('filter_id_list', models.TextField()),
                ('is_custom_sql', models.BooleanField(default=False)),
                ('custom_query', models.TextField()),
            ],
            options={
                'db_table': 'datasource_querysets',
            },
        ),
        migrations.CreateModel(
            name='DataSourceFilter',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('filter_id', models.AutoField(db_column='datasource_filter_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('hierarchy_id', models.IntegerField()),
                ('queryset_id', models.IntegerField(null=True)),
                ('col_name', models.CharField(max_length=500, null=True)),
                ('data_type', models.CharField(max_length=500, null=True)),
                ('filter_data', models.TextField(null=True)),
                ('row_data', models.TextField(null=True)),
                ('format_type', models.CharField(max_length=500, null=True)),
            ],
            options={
                'db_table': 'datasource_filters',
            },
        ),
        migrations.CreateModel(
            name='FileDetails',
            fields=[
                ('id', models.AutoField(db_column='file_details_id', primary_key=True, serialize=False)),
                ('file_type', models.PositiveBigIntegerField(db_column='file_type_id')),
                ('datapath', models.FileField(blank=True, db_column='file_data_path', max_length=1000, null=True, upload_to='insightapps/files/')),
                ('source', models.CharField(blank=True, db_column='source_path', max_length=500, null=True)),
                ('display_name', models.CharField(db_column='display_name', max_length=500, null=True)),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.PositiveBigIntegerField(db_column='user_id')),
                ('quickbooks_user_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'file_details',
            },
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.AutoField(db_column='file_type_id', primary_key=True, serialize=False)),
                ('file_type', models.CharField(db_column='file_type', max_length=50, unique=True)),
            ],
            options={
                'db_table': 'file_type',
            },
        ),
        migrations.CreateModel(
            name='functions_tb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('db_id', models.PositiveIntegerField(db_column='database_id')),
                ('function_ip', models.CharField(db_column='function', max_length=1500)),
                ('field_name', models.CharField(db_column='field_name', max_length=500)),
            ],
            options={
                'db_table': 'functions_table',
            },
        ),
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
        migrations.CreateModel(
            name='license_key',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.IntegerField()),
                ('key', models.CharField(db_column='License key', max_length=1500)),
                ('max_limit', models.IntegerField()),
                ('is_validated', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'license_keys',
            },
        ),
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(max_length=255, null=True)),
                ('angular_path', models.CharField(max_length=255, null=True)),
                ('image_urls', models.TextField(null=True)),
                ('css_classes', models.TextField(null=True)),
            ],
            options={
                'db_table': 'modules',
            },
        ),
        migrations.CreateModel(
            name='parent_ids',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('table_id', models.CharField(blank=True, db_column='table_primary_key', max_length=100, null=True)),
                ('parameter', models.CharField(blank=True, db_column='table', max_length=500, null=True)),
            ],
            options={
                'db_table': 'parent_child_table_ids',
            },
        ),
        migrations.CreateModel(
            name='previlages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('previlage', models.CharField(blank=True, max_length=2000, null=True)),
            ],
            options={
                'db_table': 'previlages',
            },
        ),
        migrations.CreateModel(
            name='QuerySets',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('queryset_id', models.AutoField(db_column='queryset_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('is_sample', models.BooleanField(default=False)),
                ('hierarchy_id', models.IntegerField()),
                ('table_names', models.TextField()),
                ('join_type', models.TextField()),
                ('joining_conditions', models.TextField()),
                ('is_custom_sql', models.BooleanField(default=False)),
                ('custom_query', models.TextField()),
                ('query_name', models.CharField(blank=True, db_column='query_name', max_length=500, null=True)),
                ('datasource_path', models.FileField(db_column='datasource_filename', null=True, upload_to='insightapps/datasource/')),
                ('datasource_json', models.URLField(db_column='datasource_json_url', null=True)),
            ],
            options={
                'db_table': 'querysets',
            },
        ),
        migrations.CreateModel(
            name='Reset_Password',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField(db_column='user_id', null=True)),
                ('key', models.CharField(blank=True, db_column='key', max_length=32)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'reset_password',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_by', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(blank=True, max_length=40, null=True)),
                ('previlage_id', models.CharField(blank=True, db_column='previlage_id', max_length=1000, null=True)),
                ('role_desc', models.CharField(default='role_description', max_length=255, null=True)),
            ],
            options={
                'db_table': 'role',
            },
        ),
        migrations.CreateModel(
            name='ServerDetails',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(db_column='server_details_id', primary_key=True, serialize=False)),
                ('server_type', models.PositiveBigIntegerField(db_column='server_type_id')),
                ('hostname', models.CharField(db_column='hostname', max_length=500, null=True)),
                ('username', models.CharField(db_column='username', max_length=500, null=True)),
                ('password', models.CharField(db_column='password', max_length=500, null=True)),
                ('database', models.CharField(db_column='database', max_length=500, null=True)),
                ('database_path', models.CharField(db_column='database_path', max_length=1500, null=True)),
                ('service_name', models.CharField(db_column='service_name', max_length=500, null=True)),
                ('port', models.IntegerField(db_column='port', null=True)),
                ('display_name', models.CharField(db_column='display_name', max_length=500, null=True)),
                ('is_connected', models.BooleanField(default=True)),
                ('is_sample', models.BooleanField(default=False)),
                ('user_id', models.IntegerField(db_column='user_id', null=True)),
            ],
            options={
                'db_table': 'server_details',
            },
        ),
        migrations.CreateModel(
            name='ServerType',
            fields=[
                ('id', models.AutoField(db_column='server_type_id', primary_key=True, serialize=False)),
                ('server_type', models.CharField(db_column='server_type', max_length=50, unique=True)),
            ],
            options={
                'db_table': 'server_type',
            },
        ),
        migrations.CreateModel(
            name='sheet_data',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(db_column='sheet_id', primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('chart_id', models.IntegerField()),
                ('server_id', models.IntegerField(blank=True, null=True)),
                ('is_sample', models.BooleanField(default=False)),
                ('file_id', models.CharField(blank=True, max_length=100, null=True)),
                ('queryset_id', models.IntegerField()),
                ('filter_ids', models.CharField(blank=True, max_length=1000, null=True)),
                ('sheet_name', models.CharField(blank=True, max_length=500, null=True)),
                ('user_ids', models.CharField(blank=True, max_length=1000, null=True)),
                ('sheet_filt_id', models.CharField(blank=True, db_column='sheetfilter_querysets_id', max_length=1000, null=True)),
                ('datapath', models.FileField(blank=True, db_column='sheet_data_path', max_length=1000, null=True, upload_to='insightapps/sheetdata/')),
                ('datasrc', models.CharField(blank=True, db_column='sheet_data_source', max_length=1000, null=True)),
                ('sheet_tag_name', models.CharField(blank=True, db_column='sheet_tag_name', max_length=1000, null=True)),
            ],
            options={
                'db_table': 'sheet_data',
            },
        ),
        migrations.CreateModel(
            name='SheetFilter_querysets',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('Sheetqueryset_id', models.AutoField(primary_key=True, serialize=False)),
                ('datasource_querysetid', models.IntegerField(blank=True, null=True)),
                ('queryset_id', models.IntegerField(blank=True, null=True)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('hierarchy_id', models.IntegerField()),
                ('filter_id_list', models.TextField(blank=True, null=True)),
                ('columns', models.TextField(blank=True, null=True)),
                ('rows', models.TextField(blank=True, null=True)),
                ('custom_query', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'sheetFilter_querysets',
            },
        ),
        migrations.CreateModel(
            name='UserConfigurations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('chart_type', models.CharField(choices=[('echart', 'Echart'), ('apex', 'Apex')], default='echart', max_length=200)),
            ],
            options={
                'db_table': 'userconfigurations',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('role_id', models.IntegerField(blank=True, db_column='role_id', null=True)),
                ('user_id', models.IntegerField(db_column='user_id')),
                ('created_by', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'user_role',
                'unique_together': {('role_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='UserGuide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('link', models.CharField(max_length=255, null=True)),
                ('alias', models.CharField(max_length=255, null=True)),
                ('module_id', models.ForeignKey(db_column='module_id', on_delete=django.db.models.deletion.CASCADE, to='dashboard.modules')),
            ],
            options={
                'db_table': 'user_guide',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(db_column='user_id', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, null=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(db_column='email_id', max_length=254, unique=True)),
                ('password', models.CharField(max_length=256)),
                ('is_active', models.BooleanField(db_column='is_active', default=False)),
                ('sub_identifier', models.CharField(max_length=100, null=True, unique=True)),
                ('country', models.CharField(max_length=20, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('demo_account', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user_profile',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
