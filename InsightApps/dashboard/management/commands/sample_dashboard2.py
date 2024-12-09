import json
from django.core.management.base import BaseCommand
from dashboard import models
import datetime
import os
import boto3
import io
from project import settings
from rest_framework.response import Response
from PIL import Image
from .storage import create_s3_file, create_s3_image, upload_sheetdata_file_to_s3

class Command(BaseCommand):
    help = 'Import JSON data into Django models'
    
    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int,
                            help='User ID for the operation')
        parser.add_argument('server_id', type=int, help='Server ID for the operation')

    def handle(self, *args, **options):
        user_id = options['user_id']  # Retrieve user_id from options
        server_id = options['server_id']  # Retrieve server_id from options

        BASE_DIR = settings.BASE_DIR
        
        # Initialize S3 client if using S3
        s3 = None
        if settings.file_save_path == 's3':
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            if not bucket_name:
                self.stdout.write(self.style.ERROR('Bucket name is not set. Please check your settings.'))
                return
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
        # Read the JSON data from the .txt file
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','datasource','Queryset-HR ATTRIITON Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)  # Load JSON data from the text file
        
        # Get current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

        # Define the output file name
        queryset_file_name = f"sample_hr_queryset_{current_datetime}.txt"
        queryset_file_key = f'insightapps/datasource/{queryset_file_name}'  # S3 key for the output file

        json_data = json.dumps(data, indent=4)
        file_buffer = io.BytesIO(json_data.encode('utf-8'))
        
        if settings.file_save_path == 's3':
            s3.upload_fileobj(file_buffer, Bucket=bucket_name, Key=queryset_file_key)
            queryset_file_url = f"https://{bucket_name}.s3.amazonaws.com/{queryset_file_key}"
        else:
            # Local storage
            media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'datasource')
            os.makedirs(media_path, exist_ok=True)
            local_path = os.path.join(media_path, queryset_file_name)
            with open(local_path, 'w') as f:
                json.dump(data, f, indent=4)
            queryset_file_url = f"{settings.file_save_url.rstrip('/')}/media/insightapps/datasource/{queryset_file_name}"
        
        querySetDefaultData={
            "user_id": user_id,
            "server_id": server_id,
            "file_id": "",
            "table_names": [['main', 'hr_attrition', 'hr_attrition']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": "SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\"",
            "query_name": "HR Attrition Data",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "datasource_path": queryset_file_key,
            "datasource_json": queryset_file_url
        }
        
        # Convert lists and other non-string data to JSON strings
        querySetDefaultData['table_names'] = json.dumps(querySetDefaultData['table_names'])
        querySetDefaultData['join_type'] = json.dumps(querySetDefaultData['join_type'])
        querySetDefaultData['joining_conditions'] = json.dumps(querySetDefaultData['joining_conditions'])

        # Create and save the QuerySets instance
        query_set_instance = models.QuerySets(
            user_id=querySetDefaultData["user_id"],
            server_id=querySetDefaultData["server_id"],
            file_id=querySetDefaultData["file_id"],
            is_sample = True,
            table_names=querySetDefaultData["table_names"],
            join_type=querySetDefaultData["join_type"],
            joining_conditions=querySetDefaultData["joining_conditions"],
            is_custom_sql=querySetDefaultData["is_custom_sql"],
            custom_query=querySetDefaultData["custom_query"],
            query_name=querySetDefaultData["query_name"],
            created_at=querySetDefaultData["created_at"],
            updated_at=querySetDefaultData["updated_at"],
            datasource_path=querySetDefaultData["datasource_path"],
            datasource_json=querySetDefaultData["datasource_json"],
        )

        query_set_instance.save()
        querysetid = models.QuerySets.objects.get(user_id=user_id,queryset_id = query_set_instance.queryset_id)
        self.stdout.write(self.style.SUCCESS('Successfully imported data into QuerySet'))
        
        
        chartFiltersData= [
            {
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name" : "attrition",
                "data_type" : "string",
                "filter_data" : "('Yes',)",
                "row_data" : "('No', 'Yes')",
                "format_type": "",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name" : "attrition",
                "data_type" : "string",
                "filter_data" : "('No',)",
                "row_data" : "('No', 'Yes')",
                "format_type": "",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name" : "gender",
                "data_type" : "string",
                "filter_data" : "('Male',)",
                "row_data" : "('Female', 'Male')",
                "format_type": "",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name" : "gender",
                "data_type" : "string",
                "filter_data" : "('Female',)",
                "row_data" : "('Female', 'Male')",
                "format_type": "",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            }
        ]
        try:
            for filter_data in chartFiltersData:
                models.ChartFilters.objects.create(
                    user_id=filter_data["user_id"],
                    server_id=filter_data["server_id"] or None,
                    file_id=filter_data["file_id"] or None,
                    datasource_querysetid=filter_data["datasource_querysetid"] or None,
                    queryset_id=filter_data["queryset_id"] or None,
                    col_name=filter_data["col_name"],
                    data_type=filter_data["data_type"],
                    filter_data=filter_data["filter_data"],
                    row_data=filter_data["row_data"],
                    format_type=filter_data["format_type"],
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Chart Filter'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        
        filter_id1 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[0]
        filter_id2 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[1]
        filter_id3 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[2]
        filter_id4 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[3]
        
        sheetFilterQuerySetData= [
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [filter_id1],
                "columns": [],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table WHERE \"attrition\" IN ('Yes')",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [filter_id2],
                "columns": [],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table WHERE \"attrition\" IN ('No')",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": ["country"],
                "rows": ['\"min(hourly_rate)\"'],
                "custom_query": "SELECT MIN(\"hourly_rate\") AS \"min(hourly_rate)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [filter_id3],
                "columns": [],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table WHERE \"gender\" IN ('Male')",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [filter_id4],
                "columns": [],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table WHERE \"gender\" IN ('Female')",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": ['\"business_travel\"'],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT \"business_travel\", COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"business_travel\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": ['\"job_role\"'],
                "rows": [' \"CNTD(id)\"', '\"avg(age)\"'],
                "custom_query": "SELECT \"job_role\", COUNT(DISTINCT \"id\") AS \"CNTD(id)\", AVG(\"age\") AS \"avg(age)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"job_role\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [' \"department\"'],
                "rows": ['\"CNTD(id)\"'],
                "custom_query": "SELECT \"department\", COUNT(DISTINCT \"id\") AS \"CNTD(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"department\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [' \"marital_status\"'],
                "rows": ['\"count(id)\"'],
                "custom_query": "SELECT \"marital_status\", COUNT(\"id\") AS \"count(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"marital_status\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },            
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [' \"attrition\"'],
                "rows": ['\"avg(years_at_company)\"'],
                "custom_query": "SELECT \"attrition\", AVG(\"years_at_company\") AS \"avg(years_at_company)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"attrition\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [' \"education_field\"'],
                "rows": ['\"sum(id)\"'],
                "custom_query": "SELECT \"education_field\", SUM(\"id\") AS \"sum(id)\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"education_field\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": [' \"attrition\"', ' \"business_travel\"', ' \"department\"', ' \"education_field\"', ' \"gender\"', ' \"job_role\"', ' \"marital_status\"', ' \"age\"', ' \"job_level\"', ' \"hourly_rate\"', ' \"daily_rate\"', ' \"monthly_rate\"', ' \"years_at_company\"', ' \"years_in_current_role\"'],
                "custom_query": "SELECT \"attrition\", \"business_travel\", \"department\", \"education_field\", \"gender\", \"job_role\", \"marital_status\", \"age\", \"job_level\", \"hourly_rate\", \"daily_rate\", \"monthly_rate\", \"years_at_company\", \"years_in_current_role\" FROM (SELECT \"hr_attrition\".\"id\" AS \"id\", \"hr_attrition\".\"age\" AS \"age\", \"hr_attrition\".\"attrition\" AS \"attrition\", \"hr_attrition\".\"business_travel\" AS \"business_travel\", \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", \"hr_attrition\".\"department\" AS \"department\", \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", \"hr_attrition\".\"education\" AS \"education\", \"hr_attrition\".\"education_field\" AS \"education_field\", \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", \"hr_attrition\".\"gender\" AS \"gender\", \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", \"hr_attrition\".\"job_level\" AS \"job_level\", \"hr_attrition\".\"job_role\" AS \"job_role\", \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", \"hr_attrition\".\"marital_status\" AS \"marital_status\", \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", \"hr_attrition\".\"over18\" AS \"over18\", \"hr_attrition\".\"over_time\" AS \"over_time\", \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" FROM \"main\".\"hr_attrition\" AS \"hr_attrition\") temp_table GROUP BY \"attrition\", \"business_travel\", \"department\", \"education_field\", \"gender\", \"job_role\", \"marital_status\", \"age\", \"job_level\", \"hourly_rate\", \"daily_rate\", \"monthly_rate\", \"years_at_company\", \"years_in_current_role\"",
                "created_at":datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
            }
        ]
        try:
            for entry in sheetFilterQuerySetData:
                # Create a new SheetFilter_querysets object
                models.SheetFilter_querysets.objects.create(
                    datasource_querysetid=int(entry.get("datasource_querysetid") or 0) if entry.get("datasource_querysetid") else None,
                    queryset_id=int(entry.get("queryset_id") or 0) if entry.get("queryset_id") else None,
                    user_id=entry.get("user_id"),
                    server_id=int(entry.get("server_id") or 0) if entry.get("server_id") else None,
                    file_id=int(entry.get("file_id") or 0) if entry.get("file_id") else None,
                    filter_id_list=json.dumps(entry.get("filter_id_list", [])),
                    columns=json.dumps(entry.get("columns", [])),
                    rows=json.dumps(entry.get("rows", [])),
                    custom_query=entry.get("custom_query"),
                    created_at=entry.get("created_at", datetime.datetime.now()),
                    updated_at=entry.get("updated_at", datetime.datetime.now()),
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported data into SheetFilter QuerySet'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
                
        sheet_filter_querysets = models.SheetFilter_querysets.objects.filter(user_id=user_id,queryset_id=querysetid.queryset_id).values_list('Sheetqueryset_id',flat=True)
        
        sheetData=[
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.1-Total Employees.txt'),
                "sheet_name" : "Total Employees",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[0],
                "sheet_tag_name" : "<p><strong>Total Employees</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.2-Attrition Count.txt'),
                "sheet_name" : "Attrition Count",
                "filter_ids" : [filter_id1],
                "sheetfilter_querysets_id" : sheet_filter_querysets[1],
                "sheet_tag_name" : "<p><strong>Attrition Count</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.3-Active Employees.txt'),
                "sheet_name" : "Active Employees",
                "filter_ids" : [filter_id2],
                "sheetfilter_querysets_id" : sheet_filter_querysets[2],
                "sheet_tag_name" : "<p><strong>Active Employees</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.4-Minimum Hourly Rate.txt'),
                "sheet_name" : "Minimum Hourly Rate",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[3],
                "sheet_tag_name" : "<p><strong>Minimum Hourly Rate</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.5-Male Employees.txt'),
                "sheet_name" : "Male Employees",
                "filter_ids" : [filter_id3],
                "sheetfilter_querysets_id" : sheet_filter_querysets[4],
                "sheet_tag_name" : "<p><strong>Male Employees</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 25,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.6-Female Employees.txt'),
                "sheet_name" : "Female Employees",
                "filter_ids" : [filter_id4],
                "sheetfilter_querysets_id" : sheet_filter_querysets[5],
                "sheet_tag_name" : "<p><strong>Female Employees</strong></p>",
                "file_id" : ""
            },
            
            {
                "user_id" : user_id,
                "chart_id" : 6,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.7-Employee Count by Business Travel Frequency.txt'),
                "sheet_name" : "Employee Count by Business Travel Frequency",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[6],
                "sheet_tag_name" : "<p><strong>Employee Count by Business Travel Frequency</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 4,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.8-Job Role  Employee Count and Average Age.txt'),
                "sheet_name" : "Job Role : Employee Count and Average Age",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[7],
                "sheet_tag_name" : "<p><strong>Job Role : Employee Count and Average Age</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 10,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.9-Employee Count by Department.txt'),
                "sheet_name" : "Employee Count by Department",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[8],
                "sheet_tag_name" : "<p><strong>Employee Count by Department</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 6,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.10-Employee Count by Marital Status.txt'),
                "sheet_name" : "Employee Count by Marital Status",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[9],
                "sheet_tag_name" : "<p><strong>Employee Count by Marital Status</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 24,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.11-Attrition Rate by Years at Company.txt'),
                "sheet_name" : "Attrition Rate by Years at Company",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[10],
                "sheet_tag_name" : "<p><strong>Attrition Rate by Years at Company</strong></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 24,
                "server_id" : server_id,
                "queryset_id" : querysetid.queryset_id,
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.12-Count of Employees by Education Field.txt'),
                "sheet_name" : "Count of Employees by Education Field",
                "filter_ids" : [],
                "sheetfilter_querysets_id" : sheet_filter_querysets[11],
                "sheet_tag_name" : "<p><strong>Count of Employees by Education Field</storage></p>",
                "file_id" : ""
            },
            {
                "user_id" : user_id,
                "chart_id" : 1,
                "server_id" : server_id,
                "file_id" : "",
                "queryset_id" : querysetid.queryset_id,
                "filter_ids" : [],
                "sheet_name" : "Attrition Details",
                "sheetfilter_querysets_id" : sheet_filter_querysets[12],
                "datasrc" : "",
                "created_at" : datetime.datetime.now(),
                "updated_at" : datetime.datetime.now(),
                "datapath" : os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','sheetdata','2.13-Attrition Details.txt'),
                "sheet_tag_name" : "<p><strong>Attrition Details</strong></p>",
                
            }
        ]

        try:
            for data in sheetData:
                # Convert lists to JSON strings
                data['filter_ids'] = json.dumps(data['filter_ids'])
                
                # Upload the file to S3
                local_file_path = data['datapath']  # Local file path
                s3_url,file_key = upload_sheetdata_file_to_s3(local_file_path,settings.AWS_STORAGE_BUCKET_NAME,data["sheetfilter_querysets_id"])

                # Update datasrc with the new S3 URL
                if s3_url:
                    data['datasrc'] = s3_url
                    data['datapath'] = file_key
                
                # Create and save the sheet_data instance
                sheet_data_instance = models.sheet_data(
                    user_id=data['user_id'],
                    chart_id=data['chart_id'],
                    server_id=data['server_id'],
                    file_id=data['file_id'],
                    is_sample = True,
                    queryset_id=data['queryset_id'],
                    filter_ids=data['filter_ids'],
                    sheet_name=data['sheet_name'],
                    sheet_filt_id=data['sheetfilter_querysets_id'],
                    datapath=data['datapath'],  # Assuming the file already exists in the given path
                    datasrc=data['datasrc'],
                    sheet_tag_name=data['sheet_tag_name'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                )
                
                sheet_data_instance.save()
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Sheet Data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        
        
        sheet_ids_list =list(models.sheet_data.objects.filter(user_id=user_id,queryset_id=querysetid.queryset_id).values_list('id', flat=True))
        
        try:
            # Define the path to the input JSON text file
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','dashboard','Dashboard-HR ATTRITION DASHBOARD.txt')   # Replace with your actual .txt file name

            # Read the JSON data from the .txt file
            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)  # Load JSON data from the text file

            # Update the sheetId in the data
            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = server_id
                item['qrySetId'] = querysetid.queryset_id

            # Upload the JSON file to S3
            file_url,output_file_key = create_s3_file(input_file_path, sheet_ids_list, server_id, querysetid, settings.AWS_STORAGE_BUCKET_NAME)
            # file_url = self.create_s3_file(data=json_data, file_name=output_file_key, bucket_name=settings.AWS_STORAGE_BUCKET_NAME)

            # Define the path to the input image file
            image_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands','dashboard','images','2024-09-20_08-09-151726819754937.jpeg')

            # Get current date and time
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

            # Upload the image to S3
            image_url ,output_image_key= create_s3_image(image_file_path, current_datetime, settings.AWS_STORAGE_BUCKET_NAME)
            # image_url = self.create_s3_image(image_path = image_file_path, image_name = output_image_key, bucket_name=settings.AWS_STORAGE_BUCKET_NAME)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return Response({"message":str(e)},status=400)
        
        dashboardSampleData = {
            "user_id": user_id,
            "server_id": [server_id],
            "queryset_id": [querysetid.queryset_id],
            "file_id": "",
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "2100",
            "width": "1350",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "HR INSIGHTS: Employee Profiles and Trends",
            "datapath": output_file_key, # Update with the new S3 file key
            "datasrc": file_url,    # Update with the new S3 file URL
            "imagepath": output_image_key,  # Update with the new S3 image key
            "imagesrc": image_url,  # Update with the new S3 image URL
            "dashboard_tag_name": "<p><strong>HR INSIGHTS: Employee Profiles and Trends</strong></p>",
            "is_public": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        try:
            dashboard_data_instance = models.dashboard_data(
                user_id=dashboardSampleData["user_id"],
                server_id=dashboardSampleData["server_id"] or None,
                queryset_id=dashboardSampleData["queryset_id"] or None,
                file_id=dashboardSampleData["file_id"] or None,
                sheet_ids=','.join(map(str, dashboardSampleData["sheet_ids"])),
                selected_sheet_ids=','.join(map(str, dashboardSampleData["selected_sheet_ids"])),
                height=dashboardSampleData["height"] or None,
                width=dashboardSampleData["width"] or None,
                grid_id=dashboardSampleData["grid_id"] or None,
                is_sample = True,
                role_ids=dashboardSampleData["role_ids"] or None,
                user_ids=','.join(map(str, dashboardSampleData["user_ids"])),
                dashboard_name=dashboardSampleData["dashboard_name"] or None,
                datapath=dashboardSampleData["datapath"] or None,
                datasrc=dashboardSampleData["datasrc"] or None,
                imagepath=dashboardSampleData["imagepath"] or None,
                imagesrc=dashboardSampleData["imagesrc"] or None,
                dashboard_tag_name=dashboardSampleData["dashboard_tag_name"] or None,
                is_public=dashboardSampleData["is_public"],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )

            dashboard_data_instance.save()
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashbaord Data'))
        except Exception as e:#
            self.stdout.write(self.style.ERROR(str(e)))