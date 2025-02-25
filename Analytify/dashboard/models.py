from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now) #, editable=False
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

def get_expiry_date():
    return timezone.now() + timedelta(days=2)


class UserProfile(AbstractUser):
    id = models.AutoField(primary_key=True,db_column='user_id')
    name = models.CharField(max_length=100,null=True)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(db_column='email_id',unique=True)
    password = models.CharField(max_length=256)
    is_active = models.BooleanField(db_column='is_active',default=False)
    sub_identifier = models.CharField(max_length=100,null=True,unique=True)
    country = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    demo_account = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table="user_profile"
        
class Account_Activation(TimeStampedModel):
    user = models.IntegerField(db_column='user_id', null=True)
    email = models.CharField(max_length=50, null=True,blank=True,default='')
    key = models.CharField(max_length=100, blank=True, null=True)
    otp = models.PositiveIntegerField()
    expiry_date = models.DateTimeField(default=get_expiry_date) #custom_expiry_date

    class Meta:
        db_table = 'account_activation'
        
class Reset_Password(models.Model):
    user = models.IntegerField(db_column='user_id', null=True)
    key = models.CharField(max_length=32, blank=True, null=False, db_column='key')
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'reset_password'

class Role(TimeStampedModel):
    role_id =models.AutoField(primary_key=True)
    created_by = models.IntegerField(null=True,blank=True)
    role = models.CharField(max_length=40,blank=True, null=True)
    previlage_id = models.CharField(max_length=1000,db_column='previlage_id',null=True,blank=True)
    role_desc = models.CharField(max_length=255, null=True,default='role_description')

    class Meta: 
        db_table = 'role'


class previlages(models.Model):
    id = models.AutoField(primary_key=True)
    previlage = models.CharField(max_length=2000,null=True,blank=True)

    class Meta:
        db_table= 'previlages'

class UserRole(TimeStampedModel):
    id = models.AutoField(primary_key=True,db_column='id')
    role_id = models.IntegerField( db_column='role_id',null=True,blank=True)
    user_id = models.IntegerField(db_column='user_id')
    created_by = models.IntegerField(null=True,blank=True)

    class Meta:
        db_table= 'user_role'
        unique_together = (('role_id', 'user_id'))


class FileType(models.Model):
    id = models.AutoField(primary_key=True,db_column='file_type_id')
    file_type = models.CharField(max_length=50,db_column='file_type',unique=True)
    
    class Meta:
        db_table = 'file_type'
    
class FileDetails(models.Model):
    id  = models.AutoField(primary_key=True,db_column='file_details_id')
    file_type = models.PositiveBigIntegerField(db_column='file_type_id')
    datapath = models.FileField(db_column='file_data_path', null=True, blank=True, upload_to='insightapps/files/',max_length=1000)
    source = models.CharField(max_length=500,null=True,blank=True,db_column='source_path')
    display_name = models.CharField(max_length=500,null=True,db_column='display_name')
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.PositiveBigIntegerField(db_column='user_id')
    quickbooks_user_id = models.CharField(max_length=100,null=True,blank=True)
    
    class Meta:
        db_table = 'file_details'

class ServerType(models.Model):
    id = models.AutoField(primary_key=True,db_column='server_type_id')
    server_type = models.CharField(max_length=50,db_column='server_type',unique=True)
    
    class Meta:
        db_table = 'server_type'
        

class ServerDetails(TimeStampedModel):
    id  = models.AutoField(primary_key=True,db_column='server_details_id')
    server_type = models.PositiveBigIntegerField(db_column='server_type_id')
    hostname = models.CharField(max_length=500,null=True,db_column='hostname')
    username = models.CharField(max_length=500,null=True,db_column='username')
    password = models.CharField(max_length=500,null=True,db_column='password')
    database = models.CharField(max_length=500,null=True,db_column='database')
    database_path = models.CharField(max_length=1500,null=True,db_column='database_path')
    service_name = models.CharField(max_length=500,null=True,db_column='service_name')
    port = models.IntegerField(null=True,db_column='port')
    display_name = models.CharField(max_length=500,null=True,db_column='display_name')
    is_connected = models.BooleanField(default=True)
    is_sample = models.BooleanField(default=False)
    user_id = models.IntegerField(null=True,db_column='user_id')
    
    class Meta:
        db_table = 'server_details'
        
class QuerySets(TimeStampedModel):
    queryset_id  = models.AutoField(primary_key=True, db_column='queryset_id')
    user_id = models.IntegerField(db_column='user_id')
    # server_id = models.IntegerField(null=True,blank=True)
    is_sample = models.BooleanField(default=False)
    # file_id = models.CharField(max_length=100,null=True,blank=True)
    hierarchy_id = models.IntegerField()
    table_names = models.TextField()
    join_type = models.TextField()
    joining_conditions = models.TextField()
    is_custom_sql = models.BooleanField(default=False)
    custom_query = models.TextField()
    query_name = models.CharField(null=True,blank=True,max_length=500,db_column = 'query_name')
    datasource_path = models.FileField(null=True,db_column='datasource_filename',upload_to='insightapps/datasource/')
    datasource_json =models.URLField(null=True,db_column = 'datasource_json_url')
    class Meta:
        db_table = 'querysets'

class DataSource_querysets(TimeStampedModel):
    datasource_querysetid = models.AutoField(primary_key=True)
    queryset_id  = models.IntegerField()
    user_id = models.IntegerField(db_column='user_id')
    # server_id = models.IntegerField(null=True,blank=True)
    # file_id = models.IntegerField(null=True,blank=True)
    hierarchy_id = models.IntegerField()
    table_names = models.TextField()
    filter_id_list = models.TextField()
    is_custom_sql = models.BooleanField(default=False)
    custom_query = models.TextField()
    
    class Meta:
        db_table = 'datasource_querysets'
        
class ChartFilters(TimeStampedModel):
    filter_id = models.AutoField(primary_key=True,db_column='filter_id')
    user_id = models.IntegerField(db_column='user_id')
    # server_id = models.IntegerField(null=True,blank=True)
    # file_id = models.IntegerField(null=True,blank=True)
    hierarchy_id = models.IntegerField()
    datasource_querysetid = models.IntegerField(null=True,blank=True)
    queryset_id  = models.IntegerField(null=True,blank=True)
    col_name = models.CharField(max_length = 500)
    data_type = models.CharField(max_length = 500)
    filter_data = models.TextField(null=True)
    row_data = models.TextField(null=True)
    format_type = models.CharField(null=True,max_length=500)
    is_exclude = models.BooleanField(default = False,null=True)
    field_logic = models.TextField(null=True,blank=True,default=None)
    is_calculated =models.BooleanField(default = False,null=True)
    top_bottom = models.TextField(null=True,blank=True,default=None)
    relative_date = models.TextField(null=True,blank=True,default=None)

    class Meta:
        db_table = 'chart_filters'

class DataSourceFilter(TimeStampedModel):
    filter_id = models.AutoField(primary_key=True,db_column='datasource_filter_id')
    user_id = models.IntegerField(db_column='user_id')
    # server_id = models.IntegerField(null=True,blank=True)
    # file_id = models.IntegerField(null=True,blank=True)
    hierarchy_id = models.IntegerField()
    queryset_id = models.IntegerField(null=True)
    col_name = models.CharField(max_length = 500,null=True)
    data_type = models.CharField(max_length = 500,null=True)
    filter_data = models.TextField(null=True)
    row_data = models.TextField(null=True)
    format_type = models.CharField(null=True,max_length=500)
    is_exclude = models.BooleanField(default = False,null=True)

    class Meta:
        db_table = 'datasource_filters'

class functions_tb(TimeStampedModel):
    db_id=models.PositiveIntegerField(db_column='database_id')
    function_ip=models.CharField(max_length=1500,db_column='function')
    field_name=models.CharField(max_length=500,db_column='field_name')

    class Meta:
        db_table = 'functions_table'



class charts(models.Model):
    chart_type=models.CharField(max_length=500,null=True)
    min_measures=models.CharField(max_length=500,null=True)
    max_measures=models.CharField(max_length=500,null=True)
    min_dimensions=models.CharField(max_length=500,null=True)
    max_dimensions=models.CharField(max_length=500,null=True)
    min_dates=models.CharField(max_length=500,null=True)
    max_dates=models.CharField(max_length=500,null=True)
    min_geo=models.CharField(max_length=500,null=True)
    max_geo=models.CharField(max_length=500,null=True)

    class Meta:
        db_table = 'charts'

# class DataSourceFilter(models.Model):
#     datasource_filter_id = models.AutoField(primary_key=True,db_column='datasource_filter_id')
#     server_id = models.IntegerField()
#     user_id = models.IntegerField()
#     queryset_id = models.IntegerField()
#     tables = models.CharField(max_length=1000)
#     alias = models.CharField(max_length=1000, default=[])
#     datatype = models.CharField(max_length=1000)
#     columns = models.CharField(max_length=1000)
#     custom_selected_data = models.CharField(max_length=1000)
#     filter_type = models.CharField(max_length=1000)
#     created_at = models.DateTimeField(default=datetime.datetime.now())
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'datasource_filters'




class license_key(TimeStampedModel):
    user_id=models.IntegerField()
    key=models.CharField(max_length=1500,db_column='License key')
    max_limit=models.IntegerField()
    is_validated=models.BooleanField(default=False)

    class Meta:
        db_table = 'license_keys'


class sheet_data(TimeStampedModel):
    id=models.AutoField(db_column='sheet_id',primary_key=True)
    user_id=models.IntegerField()
    chart_id=models.IntegerField()
    hierarchy_id = models.IntegerField(default=None)
    # server_id = models.IntegerField(null=True,blank=True)
    is_sample = models.BooleanField(default=False)
    # file_id = models.CharField(max_length=100,null=True,blank=True)
    queryset_id = models.IntegerField()
    filter_ids = models.CharField(max_length=1000,blank=True,null=True)
    sheet_name = models.CharField(max_length=500,null=True,blank=True)
    user_ids = models.CharField(max_length=1000,blank=True,null=True)
    sheet_filt_id = models.CharField(max_length=1000,blank=True,null=True,db_column='sheetfilter_querysets_id')
    datapath = models.FileField(db_column='sheet_data_path', null=True, blank=True, upload_to='insightapps/sheetdata/',max_length=1000)
    datasrc = models.CharField(max_length=1000,null=True,blank=True,db_column='sheet_data_source')
    sheet_tag_name = models.CharField(max_length=1000,null=True,blank=True,db_column='sheet_tag_name')

    class Meta:
        db_table = 'sheet_data'


class grid_type(models.Model):
    id=models.AutoField(primary_key=True)
    grid_type=models.CharField(max_length=100,db_column='grid_type')
    class Meta:
        db_table = 'grid_type'

class dashboard_data(TimeStampedModel):
    id=models.AutoField(db_column='dashboard_id',primary_key=True)
    user_id=models.IntegerField()
    # server_id = models.TextField(null=True,blank=True)
    queryset_id = models.TextField(null=True,blank=True,default=None,db_column='queryset_id')
    # file_id = models.TextField(null=True,blank=True)
    hierarchy_id = models.TextField(null=True,blank=True,default=None) 
    is_sample = models.BooleanField(default=False)
    sheet_ids = models.TextField(blank=True,null=True,db_column='saved_sheet_ids')
    selected_sheet_ids = models.TextField(blank=True,null=True,db_column='selected_sheet_ids')
    height = models.CharField(max_length=100,null=True,blank=True)
    width = models.CharField(max_length=100,null=True,blank=True)
    grid_id = models.IntegerField(null=True,blank=True)
    role_ids = models.TextField(null=True,blank=True)
    user_ids = models.TextField(blank=True,null=True)
    dashboard_name = models.CharField(max_length=1000,null=True,blank=True)
    datapath = models.FileField(db_column='dashboard_data_path', null=True, blank=True, upload_to='insightapps/dashboard/',max_length=1000)
    datasrc = models.CharField(max_length=1000,null=True,blank=True,db_column='dashboard_data_source')
    imagepath = models.ImageField(db_column='dashboard_image_path', null=True, blank=True, upload_to='insightapps/dashboard/images/',max_length=1000)
    imagesrc = models.CharField(max_length=1000,null=True,blank=True,db_column='dashboard_image_source')
    dashboard_tag_name = models.CharField(max_length=1000,null=True,blank=True,db_column='dashboard_tag_name')
    is_public = models.BooleanField(default=False,db_column='is_public')

    class Meta:
        db_table = 'dashboard_data'


class SheetFilter_querysets(TimeStampedModel):
    Sheetqueryset_id = models.AutoField(primary_key=True)
    datasource_querysetid = models.IntegerField(null=True,blank=True)
    queryset_id  = models.IntegerField(null=True,blank=True)
    user_id = models.IntegerField(db_column='user_id')
    hierarchy_id = models.IntegerField() 
    # server_id = models.IntegerField(null=True,blank=True)
    # file_id = models.IntegerField(null=True,blank=True)
    filter_id_list = models.TextField(null=True,blank=True)
    columns = models.TextField(null=True,blank=True)
    rows = models.TextField(null=True,blank=True)
    custom_query = models.TextField(null=True,blank=True)
    pivot_measure = models.TextField(null=True,blank=True)
    
    class Meta:
        db_table = 'sheetFilter_querysets'



class DashboardFilters(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    dashboard_id = models.IntegerField(null=True,blank=True)
    sheet_id_list = models.CharField(max_length=200,null=True,blank=True)
    filter_name = models.CharField(max_length=200,null=True)
    table_name = models.CharField(max_length=200,null=True)
    column_name = models.CharField(max_length=200,null=True)
    selected_query = models.IntegerField(null=True,blank=True)
    column_datatype = models.CharField(max_length=200,null=True)
    queryset_id = models.TextField(null=True,blank=True)
    hierarchy_id = models.IntegerField(null=True)
    
    

    class Meta:
        db_table = 'dashboard_filters'



class parent_ids(models.Model):
    id=models.AutoField(primary_key=True)
    table_id=models.CharField(max_length=100,null=True,blank=True,db_column='table_primary_key')
    # table_id=models.IntegerField(null=True,blank=True,db_column='table_primary_key')
    parameter=models.CharField(max_length=500,null=True,blank=True,db_column='table')
    is_cross_database=models.BooleanField(default=False)

    class Meta:
        db_table = 'parent_child_table_ids'


class cross_db_ids(models.Model):
    id=models.AutoField(primary_key=True)
    hierarchy_ids = models.TextField(blank=True,null=True,db_column='hierarchy_ids')
    class Meta:
        db_table = 'cross_database_ids'
        

class Modules(models.Model):
    module_name = models.CharField(max_length=255,null=True)
    angular_path = models.CharField(max_length=255,null=True)
    image_urls = models.TextField(null=True)
    css_classes = models.TextField(null=True)

    class Meta:
        db_table = 'modules'

class UserGuide(TimeStampedModel):
    title = models.CharField(max_length=255,null=True)
    description = models.CharField(max_length=255,null=True)
    link = models.CharField(max_length=255,null=True)
    alias = models.CharField(max_length=255,null=True)
    module_id = models.ForeignKey(Modules,on_delete=models.CASCADE,db_column='module_id')

    class Meta:
        db_table = 'user_guide'

class UserConfigurations(TimeStampedModel):
    user_id = models.IntegerField(db_column='user_id')
    
    CHART_TYPE = [
        ('echart', 'Echart'),
        ('apex', 'Apex')
    ]
    chart_type = models.CharField(max_length=200, choices=CHART_TYPE, default='echart')
    
    class Meta:
        db_table = 'user_chart_plugins'

class Custome_theme_data(TimeStampedModel):
    custom_theme_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(db_column='user_id')
    navigation_styles = models.CharField(max_length=500,null=True,blank=True,db_column="navigation_styles")
    primary_colour_theme = models.CharField(max_length=500,null=True,blank=True,db_column="primary_colour_theme")
    menu_colours = models.CharField(max_length=500,null=True,blank=True,db_column="menu_colours")
    header_colours = models.CharField(max_length=500,null=True,blank=True,db_column="header_colours")
    background_colour = models.CharField(max_length=500,null=True,blank=True,db_column="background_colour")
    menutype = models.CharField(max_length=500,null=True,blank=True,db_column="menutype")
    headertype = models.CharField(max_length=500,null=True,blank=True,db_column="headertype")
    textcolour = models.CharField(max_length=500,null=True,blank=True,db_column="textcolour")
    

    class Meta:
        db_table = 'custome_theme_data' 



class calculation_field(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True,blank=True)
    queryset_id  = models.IntegerField(null=True,blank=True)
    # server_id = models.IntegerField(null=True,blank=True)
    # file_id = models.IntegerField(null=True,blank=True)
    hierarchy_id = models.IntegerField(default=None)
    field_name = models.CharField(max_length=500,null=True,blank=True)
    nestedFunctionName = models.CharField(max_length=500,null=True,blank=True)
    functionName = models.CharField(max_length=500,null=True,blank=True)
    cal_logic = models.TextField(null=True,blank=True,db_column='calculation_logic')
    actual_dragged_logic = models.TextField(null=True,blank=True)

    class Meta:
        db_table = 'calculation_field'

class Dashboard_drill_through(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    action_name = models.CharField(max_length=500,null=True,blank=True)
    queryset_id = models.TextField(null=True,blank=True)
    dashboard_id = models.IntegerField(null=True,blank=True)
    source_sheet_id = models.IntegerField(null=True,blank=True,db_column='source_sheet_id')
    target_sheet_id = models.TextField(null=True,blank=True,db_column='target_sheet_id')
    hierarchy_id = models.IntegerField(null=True,blank=True)


    class Meta:
        db_table = 'dashboard_drill_through_data' 