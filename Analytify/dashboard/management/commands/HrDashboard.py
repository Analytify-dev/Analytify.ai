import json
from django.core.management.base import BaseCommand
from dashboard import models
import datetime
import io
import os
import boto3
from PIL import Image
from project import settings
from rest_framework.response import Response
from .storage import create_s3_file, create_s3_image, upload_sheetdata_file_to_s3


class Command(BaseCommand):
    help = 'Import JSON data into Django models'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID for the operation')
    
        parser.add_argument('hierarchy_id', type=int, help='Server ID for the operation')
        
    def handle(self, *args, **options):
        user_id = options['user_id']
        hierarchy_id = options['hierarchy_id']
        
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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-HR ATTRIITON Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
        queryset_file_name = f"sample_hr_queryset_{current_datetime}.txt"
        queryset_file_key = f'insightapps/datasource/{queryset_file_name}'

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


        querySetDefaultData = {
            "user_id": user_id,
            "hierarchy_id":hierarchy_id,
            "table_names": [['In Ex', 'hr_attrition', 'hr_attrition']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": """
                                SELECT 
                                    \"hr_attrition\".\"id\" AS \"id\", 
                                    \"hr_attrition\".\"age\" AS \"age\", 
                                    \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                    \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                    \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                    \"hr_attrition\".\"department\" AS \"department\", 
                                    \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                    \"hr_attrition\".\"education\" AS \"education\", 
                                    \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                    \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                    \"hr_attrition\".\"gender\" AS \"gender\", 
                                    \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                    \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                    \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                    \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                    \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                    \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                    \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                    \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                    \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                    \"hr_attrition\".\"over18\" AS \"over18\", 
                                    \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                    \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                    \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                    \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                    \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                    \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                    \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                    \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                    \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                    \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                    \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                    \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                    \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                FROM 
                                    \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                """,
            "query_name": "HR Analytics",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "datasource_path": queryset_file_key,
            "datasource_json": queryset_file_url
        }

        
        querySetDefaultData['table_names'] = json.dumps(querySetDefaultData['table_names'])
        querySetDefaultData['join_type'] = json.dumps(querySetDefaultData['join_type'])
        querySetDefaultData['joining_conditions'] = json.dumps(querySetDefaultData['joining_conditions'])

        query_set_instance = models.QuerySets(
            user_id=querySetDefaultData["user_id"],
            hierarchy_id=querySetDefaultData["hierarchy_id"],
            is_sample=True,
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
        querysetid = models.QuerySets.objects.get(user_id=user_id, queryset_id=query_set_instance.queryset_id)
        self.stdout.write(self.style.SUCCESS('Successfully imported data into QuerySet'))
        
        chartFiltersData = [
            {
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "attrition",
                "data_type": "string",
                "filter_data": "('Yes',)",
                "row_data": "('No', 'Yes')",
                "format_type": "",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "attrition",
                "data_type": "string",
                "filter_data": "('No',)",
                "row_data": "('No', 'Yes')",
                "format_type": "",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "gender",
                "data_type": "string",
                "filter_data": "('Male',)",
                "row_data": "('Female', 'Male')",
                "format_type": "",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "gender",
                "data_type": "string",
                "filter_data": "('Female',)",
                "row_data": "('Female', 'Male')",
                "format_type": "",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "attrition",
                "data_type": "string",
                "filter_data": "('Yes',)",
                "row_data": "('No', 'Yes')",
                "format_type": "",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]
        try:
            for filter_data in chartFiltersData:
                models.ChartFilters.objects.create(
                    user_id=filter_data["user_id"],
                    hierarchy_id=filter_data["hierarchy_id"] or None,
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
            pass
        
        filter_id1 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[0]
        filter_id2 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[1]
        filter_id3 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[2]
        filter_id4 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[3]
        filter_id5 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[4]
        sheetFilterQuerySetData = [
            # Total Employees
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ['"count(id)"'],
                "custom_query": """
                                SELECT COUNT(\"id\") AS \"count(id)\" 
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Count
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [filter_id1],
                "columns": [],
                "rows": ['"count(attrition)"'],
                "custom_query": """
                                SELECT COUNT(\"attrition\") AS \"count(attrition)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    WHERE \"attrition\" IN ('Yes')
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Active Employees
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [filter_id2],
                "columns": [],
                "rows": ['"count(attrition)"'],
                "custom_query": """
                                SELECT COUNT(\"attrition\") AS \"count(attrition)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    WHERE \"attrition\" IN ('No')
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Maximum Hourly Rate
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ['"max(hourly_rate)"'],
                "custom_query": """ 
                                    SELECT MAX(\"hourly_rate\") AS \"max(hourly_rate)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },     
            # Male Employees           
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [filter_id3],
                "columns": [],
                "rows": ['"count(gender)"'],
                "custom_query": """ 
                                    SELECT COUNT(\"gender\") AS \"count(gender)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    WHERE \"gender\" IN ('Male')
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },      
            # Female Employees
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [filter_id4],
                "columns": [],
                "rows": ['"count(gender)"'],
                "custom_query": """ SELECT COUNT(\"gender\") AS \"count(gender)\"
                                        FROM (
                                            SELECT 
                                                \"hr_attrition\".\"id\" AS \"id\", 
                                                \"hr_attrition\".\"age\" AS \"age\", 
                                                \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                                \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                                \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                                \"hr_attrition\".\"department\" AS \"department\", 
                                                \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                                \"hr_attrition\".\"education\" AS \"education\", 
                                                \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                                \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                                \"hr_attrition\".\"gender\" AS \"gender\", 
                                                \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                                \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                                \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                                \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                                \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                                \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                                \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                                \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                                \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                                \"hr_attrition\".\"over18\" AS \"over18\", 
                                                \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                                \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                                \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                                \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                                \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                                \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                                \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                                \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                                \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                                \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                                \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                                \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                                \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                            FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                        ) temp_table 
                                        WHERE \"gender\" IN ('Female') 
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition By Education Field
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [filter_id5],
                "columns": [' "education_field"'],
                "rows": ['"count(id)"'],
                "custom_query": """
                                SELECT \"education_field\" AS \"education_field\", COUNT(\"id\") AS \"count(id)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    WHERE \"attrition\" IN ('Yes') 
                                    GROUP BY \"education_field\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Job Role : Employee Count and Average Age
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"job_role"'],
                "rows": ['"count(id)"', '"avg(age)"'],
                "custom_query": """
                                    SELECT \"job_role\" AS \"job_role\", COUNT(\"id\") AS \"count(id)\", AVG(\"age\") AS \"avg(age)\"
                                        FROM (
                                            SELECT 
                                                \"hr_attrition\".\"id\" AS \"id\", 
                                                \"hr_attrition\".\"age\" AS \"age\", 
                                                \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                                \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                                \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                                \"hr_attrition\".\"department\" AS \"department\", 
                                                \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                                \"hr_attrition\".\"education\" AS \"education\", 
                                                \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                                \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                                \"hr_attrition\".\"gender\" AS \"gender\", 
                                                \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                                \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                                \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                                \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                                \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                                \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                                \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                                \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                                \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                                \"hr_attrition\".\"over18\" AS \"over18\", 
                                                \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                                \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                                \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                                \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                                \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                                \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                                \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                                \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                                \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                                \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                                \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                                \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                                \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                            FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                        ) temp_table 
                                        GROUP BY \"job_role\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Employee Count By Department
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"department"'],
                "rows": ['"count(id)"'],
                "custom_query": """
                                SELECT \"department\" AS \"department\", COUNT(\"id\") AS \"count(id)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    GROUP BY \"department\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },     
            # Employee count By Marital Status
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"marital_status"'],
                "rows": ['"count(id)"'],
                "custom_query": """
                                SELECT \"marital_status\" AS \"marital_status\", COUNT(\"id\") AS \"count(id)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    GROUP BY \"marital_status\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Rate by Years at Company
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"attrition"'],
                "rows": ['"sum(years_at_company)"'],
                "custom_query": """
                                    SELECT \"attrition\" AS \"attrition\", SUM(\"years_at_company\") AS \"sum(years_at_company)\"
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    GROUP BY \"attrition\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Details
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"id"', '"attrition"', '"business_travel"', '"department"', '"education_field"', '"gender"', '"job_role"', '"marital_status"', '"hourly_rate"'],
                "rows": [],
                "custom_query": """
                                    SELECT 
                                        \"id\" AS \"id\", 
                                        \"attrition\" AS \"attrition\", 
                                        \"business_travel\" AS \"business_travel\", 
                                        \"department\" AS \"department\", 
                                        \"education_field\" AS \"education_field\", 
                                        \"gender\" AS \"gender\", 
                                        \"job_role\" AS \"job_role\", 
                                        \"marital_status\" AS \"marital_status\", 
                                        \"hourly_rate\" AS \"hourly_rate\" 
                                    FROM (
                                        SELECT 
                                            \"hr_attrition\".\"id\" AS \"id\", 
                                            \"hr_attrition\".\"age\" AS \"age\", 
                                            \"hr_attrition\".\"attrition\" AS \"attrition\", 
                                            \"hr_attrition\".\"business_travel\" AS \"business_travel\", 
                                            \"hr_attrition\".\"daily_rate\" AS \"daily_rate\", 
                                            \"hr_attrition\".\"department\" AS \"department\", 
                                            \"hr_attrition\".\"distance_from_home\" AS \"distance_from_home\", 
                                            \"hr_attrition\".\"education\" AS \"education\", 
                                            \"hr_attrition\".\"education_field\" AS \"education_field\", 
                                            \"hr_attrition\".\"environment_satisfaction\" AS \"environment_satisfaction\", 
                                            \"hr_attrition\".\"gender\" AS \"gender\", 
                                            \"hr_attrition\".\"hourly_rate\" AS \"hourly_rate\", 
                                            \"hr_attrition\".\"job_involvement\" AS \"job_involvement\", 
                                            \"hr_attrition\".\"job_level\" AS \"job_level\", 
                                            \"hr_attrition\".\"job_role\" AS \"job_role\", 
                                            \"hr_attrition\".\"job_satisfaction\" AS \"job_satisfaction\", 
                                            \"hr_attrition\".\"marital_status\" AS \"marital_status\", 
                                            \"hr_attrition\".\"monthly_income\" AS \"monthly_income\", 
                                            \"hr_attrition\".\"monthly_rate\" AS \"monthly_rate\", 
                                            \"hr_attrition\".\"num_companies_worked\" AS \"num_companies_worked\", 
                                            \"hr_attrition\".\"over18\" AS \"over18\", 
                                            \"hr_attrition\".\"over_time\" AS \"over_time\", 
                                            \"hr_attrition\".\"percent_salary_hike\" AS \"percent_salary_hike\", 
                                            \"hr_attrition\".\"performance_rating\" AS \"performance_rating\", 
                                            \"hr_attrition\".\"relationship_satisfaction\" AS \"relationship_satisfaction\", 
                                            \"hr_attrition\".\"standard_hours\" AS \"standard_hours\", 
                                            \"hr_attrition\".\"stock_option_level\" AS \"stock_option_level\", 
                                            \"hr_attrition\".\"total_working_years\" AS \"total_working_years\", 
                                            \"hr_attrition\".\"training_times_last_year\" AS \"training_times_last_year\", 
                                            \"hr_attrition\".\"work_life_balance\" AS \"work_life_balance\", 
                                            \"hr_attrition\".\"years_at_company\" AS \"years_at_company\", 
                                            \"hr_attrition\".\"years_in_current_role\" AS \"years_in_current_role\", 
                                            \"hr_attrition\".\"years_since_last_promotion\" AS \"years_since_last_promotion\", 
                                            \"hr_attrition\".\"years_with_current_manager\" AS \"years_with_current_manager\" 
                                        FROM \"In Ex\".\"hr_attrition\" AS \"hr_attrition\"
                                    ) temp_table 
                                    GROUP BY 
                                        \"id\", 
                                        \"attrition\", 
                                        \"business_travel\", 
                                        \"department\", 
                                        \"education_field\", 
                                        \"gender\", 
                                        \"job_role\", 
                                        \"marital_status\", 
                                        \"hourly_rate\", 
                                        \"id\", 
                                        \"attrition\", 
                                        \"business_travel\", 
                                        \"department\", 
                                        \"education_field\", 
                                        \"gender\", 
                                        \"job_role\", 
                                        \"marital_status\", 
                                        \"hourly_rate\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]
        try:
            for entry in sheetFilterQuerySetData:
                models.SheetFilter_querysets.objects.create(
                    datasource_querysetid=int(entry.get("datasource_querysetid") or 0) if entry.get("datasource_querysetid") else None,
                    queryset_id=int(entry.get("queryset_id") or 0) if entry.get("queryset_id") else None,
                    user_id=entry.get("user_id"),
                    hierarchy_id=int(entry.get("hierarchy_id") or 0) if entry.get("hierarchy_id") else None,
                    filter_id_list=json.dumps(entry.get("filter_id_list", [])),
                    columns=json.dumps(entry.get("columns", [])),
                    rows=json.dumps(entry.get("rows", [])),
                    custom_query=entry.get("custom_query"),
                    created_at=entry.get("created_at", datetime.datetime.now()),
                    updated_at=entry.get("updated_at", datetime.datetime.now()),
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported data into SheetFilter QuerySet'))
        except Exception as e:
            pass

        sheet_filter_querysets = models.SheetFilter_querysets.objects.filter(user_id=user_id, queryset_id=querysetid.queryset_id).values_list('Sheetqueryset_id', flat=True)
        sheetData = [
            # Total Employees
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.1-Total Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Employees</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Count
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id1],
                "sheet_name": "Attrition Count",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.2-Attrition Count.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Attrition Count</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Active Employees
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id2],
                "sheet_name": "Active Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.3-Active Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Active Employees</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Maximum Hourly Rate
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Maximum Hourly Rate",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.4-Minimum Hourly Rate.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Maximum Hourly Rate</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Male Employees
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id3],
                "sheet_name": "Male Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.5-Male Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Male Employees</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Female Employees
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id4],
                "sheet_name": "Female Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.6-Female Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Female Employees</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition By Education Field
            {
                "user_id": user_id,
                "chart_id": 10,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id5],
                "sheet_name": "Attrition By Education Field",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.7-Attrition By Education Field.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Attrition By Education Field</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Job Role : Employee Count and Average Age
            {
                "user_id": user_id,
                "chart_id": 4,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Job Role : Employee Count and Average Age",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.8-Job Role  Employee Count and Average Age.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Job Role : Employee Count and Average Age</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Employee Count By Department
            {
                "user_id": user_id,
                "chart_id": 27,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Employee Count By Department",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.9-Employee Count by Department.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Employee Count By Department</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Employee count By Marital Status
            {
                "user_id": user_id,
                "chart_id": 3,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Employee count By Marital Status",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.10-Employee Count by Marital Status.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Employee count By Marital Status</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Rate by Years at Company
            {
                "user_id": user_id,
                "chart_id": 24,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Attrition Rate by Years at Company",
                "sheetfilter_querysets_id": sheet_filter_querysets[10],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.11-Attrition Rate by Years at Company.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Attrition Rate by Years at Company</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Attrition Details
            {
                "user_id": user_id,
                "chart_id": 1,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Attrition Details",
                "sheetfilter_querysets_id": sheet_filter_querysets[11],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '2.12-Attrition Details.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Attrition Details</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]
        try:
            for data in sheetData:
                data['filter_ids'] = json.dumps(data['filter_ids'])
                
                local_file_path = data['datapath']
                if settings.file_save_path == 's3':
                    s3_url, file_key = upload_sheetdata_file_to_s3(local_file_path, bucket_name, data['sheetfilter_querysets_id'])
                    if s3_url:
                        data['datasrc'] = s3_url
                        data['datapath'] = file_key
                else:
                    # Local storage
                    media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'sheetdata')
                    os.makedirs(media_path, exist_ok=True)
                    local_path = os.path.join(media_path, os.path.basename(local_file_path))
                    with open(local_file_path, 'r') as f:
                        file_data = json.load(f)
                    with open(local_path, 'w') as f:
                        json.dump(file_data, f, indent=4)
                    data['datasrc'] = f"{settings.file_save_url.rstrip('/')}/media/insightapps/sheetdata/{os.path.basename(local_file_path)}"
                    data['datapath'] = local_path
                
                sheet_data_instance = models.sheet_data(
                    user_id=data['user_id'],
                    chart_id=data['chart_id'],
                    hierarchy_id=data['hierarchy_id'],
                    is_sample=True,
                    queryset_id=data['queryset_id'],
                    filter_ids=data['filter_ids'],
                    sheet_name=data['sheet_name'],
                    sheet_filt_id=data['sheetfilter_querysets_id'],
                    datapath=data['datapath'],
                    datasrc=data['datasrc'],
                    sheet_tag_name=data['sheet_tag_name'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                )
                
                sheet_data_instance.save()
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Sheet Data'))
        except Exception as e:
            pass
        
        sheet_ids_list = list(models.sheet_data.objects.filter(user_id=user_id, queryset_id=querysetid.queryset_id).values_list('id', flat=True).order_by('id'))
        
        try:
            input_file_name = 'Dashboard-HR ATTRITION DASHBOARD.txt'
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', input_file_name)

            # Read the JSON data from the .txt file
            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)  # Load JSON data from the text file

            # Update the sheetId in the data
            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = hierarchy_id
                item['qrySetId'] = querysetid.queryset_id

            if settings.file_save_path == 's3':
                file_url, output_file_key = create_s3_file(input_file_path, sheet_ids_list, hierarchy_id, querysetid, bucket_name)
            else:
                media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'datasource')
                os.makedirs(media_path, exist_ok=True)
                local_path = os.path.join(media_path, input_file_name)
                with open(local_path, 'w') as f:
                    json.dump(data, f, indent=4)
                file_url = f"{settings.file_save_url.rstrip('/')}/media/insightapps/datasource/{input_file_name}"
                output_file_key = local_path

            image_file_name = 'HrDashboardImage.jpeg'
            image_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'images', image_file_name)
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

            if settings.file_save_path == 's3':
                image_url, output_image_key = create_s3_image(image_file_path, current_datetime, bucket_name)
            else:
                import shutil  # Added to copy files instead of renaming
                image_media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'images')
                os.makedirs(image_media_path, exist_ok=True)
                local_image_path = os.path.join(image_media_path, image_file_name)
                # os.rename(image_file_path, local_image_path)
                shutil.copy2(image_file_path, local_image_path)  # Copy instead of rename
                image_url = f"{settings.file_save_url.rstrip('/')}/media/insightapps/images/{image_file_name}"
                output_image_key = local_image_path
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return Response({"message": str(e)}, status=400)

        dashboardSampleData = {
            "user_id": user_id,
            "hierarchy_id":[hierarchy_id],
            "queryset_id": [querysetid.queryset_id],
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "1400",
            "width": "1000",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "HR INSIGHTS: Employee Profiles and Trends",
            "datapath": output_file_key,
            "datasrc": file_url,
            "imagepath": output_image_key,
            "imagesrc": image_url,
            "dashboard_tag_name": """<p style="text-align:center;"><span style="color:hsl(0, 0%, 0%);font-size:16px;"><strong>HR INSIGHTS: Employee Profiles and Trends</strong></span></p>""",
            "is_public": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        try:
            dashboard_data_instance = models.dashboard_data(
                user_id=dashboardSampleData["user_id"],
                hierarchy_id=dashboardSampleData["hierarchy_id"] or None,
                queryset_id=dashboardSampleData["queryset_id"] or None,
                sheet_ids=','.join(map(str, dashboardSampleData["sheet_ids"])),
                selected_sheet_ids=','.join(map(str, dashboardSampleData["selected_sheet_ids"])),
                height=dashboardSampleData["height"] or None,
                width=dashboardSampleData["width"] or None,
                grid_id=dashboardSampleData["grid_id"] or None,
                is_sample=True,
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
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashboard Data'))
        except Exception as e:
            pass
        # dashbaordFiltersSampleData = [
        #     {
        #         "user_id": user_id,
        #         "dashboard_id": dashboard_data_instance.id,
        #         "sheet_id_list": sheet_ids_list,
        #         "filter_name": "Department",
        #         "table_name": "hr_attrition",
        #         "column_name": "department",
        #         "column_datatype": "string",
        #         "hierarchy_id" : hierarchy_id,
        #         "queryset_id": [querysetid.queryset_id],
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "dashboard_id": dashboard_data_instance.id,
        #         "sheet_id_list": sheet_ids_list,
        #         "filter_name": "Gender",
        #         "table_name": "hr_attrition",
        #         "column_name": "gender",
        #         "column_datatype": "string",
        #         "hierarchy_id" : hierarchy_id,
        #         "queryset_id": [querysetid.queryset_id],
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "dashboard_id": dashboard_data_instance.id,
        #         "sheet_id_list": sheet_ids_list,
        #         "filter_name": "Job Role",
        #         "table_name": "hr_attrition",
        #         "column_name": "job_role",
        #         "column_datatype": "string",
        #         "hierarchy_id" : hierarchy_id,
        #         "queryset_id": [querysetid.queryset_id],
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     }
        # ]
        # try:
        #     for filter_data in dashbaordFiltersSampleData:
        #         models.DashboardFilters.objects.create(
        #             user_id=filter_data["user_id"],
        #             dashboard_id=filter_data["dashboard_id"],
        #             sheet_id_list=','.join(map(str, filter_data["sheet_id_list"])),
        #             filter_name=filter_data["filter_name"],
        #             table_name=filter_data["table_name"],
        #             column_name=filter_data["column_name"],
        #             column_datatype=filter_data["column_datatype"],
        #             hierarchy_id=filter_data["hierarchy_id"],
        #             selected_query = querysetid.queryset_id,
        #             queryset_id=filter_data["queryset_id"] or None,
        #             created_at=datetime.datetime.now(),
        #             updated_at=datetime.datetime.now(),
        #         )
            
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashboard Filter Data'))
        # except Exception as e:
        #     pass