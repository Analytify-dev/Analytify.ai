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
        parser.add_argument('server_id', type=int, help='Server ID for the operation')
        
    def handle(self, *args, **options):
        user_id = options['user_id']
        server_id = options['server_id']
        
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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-Employees Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)
        
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
        queryset_file_name = f"sample_employee_queryset_{current_datetime}.txt"
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
            "server_id": server_id,
            "table_names": [["main", "employees", "employees"]],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": "SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\"",
            "query_name": "Employees Data",
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
            server_id=querySetDefaultData["server_id"],
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
                "server_id": server_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "gender",
                "data_type": "varchar",
                "filter_data": "('Female',)",
                "row_data": "('Female', 'Male')",
                "format_type": "%m/%d/%Y",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "server_id": server_id,
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "col_name": "gender",
                "data_type": "varchar",
                "filter_data": "('Male',)",
                "row_data": "('Female', 'Male')",
                "format_type": "%m/%d/%Y",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]
        try:
            for filter_data in chartFiltersData:
                models.ChartFilters.objects.create(
                    user_id=filter_data["user_id"],
                    server_id=filter_data["server_id"] or None,
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
        
        sheetFilterQuerySetData = [
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ["count(eeid)"],
                "custom_query": """SELECT COUNT(\"eeid\") AS \"count(eeid)\"
                            FROM (
                            SELECT 
                                \"employees\".\"eeid\" AS \"eeid\",
                                \"employees\".\"full_name\" AS \"full_name\",
                                \"employees\".\"job_title\" AS \"job_title\",
                                \"employees\".\"department\" AS \"department\",
                                \"employees\".\"business_unit\" AS \"business_unit\",
                                \"employees\".\"gender\" AS \"gender\",
                                \"employees\".\"ethnicity\" AS \"ethnicity\",
                                \"employees\".\"age\" AS \"age\",
                                \"employees\".\"hire_date\" AS \"hire_date\",
                                \"employees\".\"annual_salary\" AS \"annual_salary\",
                                \"employees\".\"bonus_percentage\" AS \"bonus_percentage\",
                                \"employees\".\"country\" AS \"country\",
                                \"employees\".\"city\" AS \"city\"
                            FROM \"main\".\"employees\" AS \"employees\"
                            ) temp_table""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [filter_id1],
                "columns": [],
                "rows": ["count(eeid)"],
                "custom_query": "SELECT COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table WHERE \"gender\" IN ('Female')",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [filter_id2],
                "columns": [],
                "rows": ["count(eeid)"],
                "custom_query": "SELECT COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table WHERE \"gender\" IN ('Male')",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ['"avg(bonus_percentage)"'],
                "custom_query": "SELECT AVG(\"bonus_percentage\") AS \"avg(bonus_percentage)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": ['"department"'],
                "rows": ['"avg(annual_salary)"'],
                "custom_query": "SELECT \"department\", AVG(\"annual_salary\") AS \"avg(annual_salary)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"department\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },            
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": ['"country"'],
                "rows": ['"count(eeid)"'],
                "custom_query": "SELECT \"country\", COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"country\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": ['"gender"'],
                "rows": ['"avg(annual_salary)"'],
                "custom_query": "SELECT \"gender\", AVG(\"annual_salary\") AS \"avg(annual_salary)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"gender\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": ['"gender"'],
                "rows": ['"count(eeid)"'],
                "custom_query": "SELECT \"gender\", COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"gender\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": ['"hire_date"'],
                "rows": ['"sum(bonus_percentage)"'],
                "custom_query": "SELECT STRFTIME('%Y', \"hire_date\") AS \"hire_date:OK\", SUM(\"bonus_percentage\") AS \"sum(bonus_percentage)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"hire_date:OK\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },                
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": [' "department"'],
                "rows": ['"count(eeid)"'],
                "custom_query": "SELECT \"department\", COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"department\"",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                "filter_id_list": [],
                "columns": [' "eeid"', ' "full_name"', ' "department"', ' "job_title"', ' "gender"', ' "business_unit"', ' "ethnicity"', '"hire_date"', ' "country"', ' "age"', ' "annual_salary"', ' "bonus_percentage"'],
                "rows": [],
                "custom_query": "SELECT \"eeid\", \"full_name\", \"department\", \"job_title\", \"gender\", \"business_unit\", \"ethnicity\", STRFTIME('%Y', \"hire_date\") AS \"hire_date:OK\", \"country\", \"age\", \"annual_salary\", \"bonus_percentage\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"eeid\", \"full_name\", \"department\", \"job_title\", \"gender\", \"business_unit\", \"ethnicity\", \"hire_date:OK\", \"country\", \"age\", \"annual_salary\", \"bonus_percentage\"",
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
                    server_id=int(entry.get("server_id") or 0) if entry.get("server_id") else None,
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
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.1-Total Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Total Employees</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id1],
                "sheet_name": "Female Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.2-Female Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Female Employees</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [filter_id2],
                "sheet_name": "Male Employees",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.3-Male Employees.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Male Employees</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Average Bonus Percentage",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.4-Average Bonus Percentage.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Average Bonus Percentage</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 6,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Average Annual Salary by Department",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.5-Average Annual Salary by Department.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Average Annual Salary by Department</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 24,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Country Wise Employee Count",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.6-Country Wise Employee Count.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Country Wise Employee Count</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 6,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Average Annual Salary by Gender",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.7-Average Annual Salary by Gender.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Average Annual Salary by Gender</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 24,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Gender Distribution",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.8-Gender Distribution.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p>Gender Distribution</p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 13,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Bonus Percentage Over Time",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.9-Bonus Percentage Over Time.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Bonus Percentage Over Time</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 10,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Number of Employees by Department",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.10-Number of Employees by Department.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Number of Employees by Department</strong></p>",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 1,
                "server_id": server_id,
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Employee Details",
                "sheetfilter_querysets_id": sheet_filter_querysets[10],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '1.11-Employee Details.txt'),
                "datasrc": "",
                "sheet_tag_name": "<p><strong>Employee Details</strong></p>",
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
                    server_id=data['server_id'],
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
        
        sheet_ids_list = list(models.sheet_data.objects.filter(user_id=user_id, queryset_id=querysetid.queryset_id).values_list('id', flat=True))
        
        try:
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'Dashboard-EMPLOYEE SAMPLE DASHBOARD.txt')

            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)

            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = server_id
                item['qrySetId'] = querysetid.queryset_id

            file_url, output_file_key = create_s3_file(input_file_path, sheet_ids_list, server_id, querysetid, bucket_name)

            image_image_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'images', '2024-09-20_08-04-431726819483393.jpeg')

            current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

            image_url, output_image_key = create_s3_image(image_image_path, current_datetime, bucket_name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return Response({"message": str(e)}, status=400)
        
        dashboardSampleData = {
            "user_id": user_id,
            "server_id": [server_id],
            "queryset_id": [querysetid.queryset_id],
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "2100",
            "width": "1000",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "EMPLOYEE SAMPLE DASHBOARD",
            "datapath": output_file_key,
            "datasrc": file_url,
            "imagepath": output_image_key,
            "imagesrc": image_url,
            "dashboard_tag_name": "<p><strong>EMPLOYEE SAMPLE DASHBOARD</strong></p>",
            "is_public": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        try:
            dashboard_data_instance = models.dashboard_data(
                user_id=dashboardSampleData["user_id"],
                server_id=dashboardSampleData["server_id"] or None,
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
        
        dashbaordFiltersSampleData = [
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list[4:],
                "filter_name": "Country",
                "table_name": "employees",
                "column_name": "country",
                "column_datatype": "string",
                "queryset_id": querysetid.queryset_id,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list[4:],
                "filter_name": "Department",
                "table_name": "employees",
                "column_name": "department",
                "column_datatype": "string",
                "queryset_id": querysetid.queryset_id,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list[4:],
                "filter_name": "Gender",
                "table_name": "employees",
                "column_name": "gender",
                "column_datatype": "string",
                "queryset_id": querysetid.queryset_id,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]
        try:
            for filter_data in dashbaordFiltersSampleData:
                models.DashboardFilters.objects.create(
                    user_id=filter_data["user_id"],
                    dashboard_id=filter_data["dashboard_id"],
                    sheet_id_list=','.join(map(str, filter_data["sheet_id_list"])),
                    filter_name=filter_data["filter_name"],
                    table_name=filter_data["table_name"],
                    column_name=filter_data["column_name"],
                    column_datatype=filter_data["column_datatype"],
                    queryset_id=filter_data["queryset_id"] or None,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )
            
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashboard Filter Data'))
        except Exception as e:
            pass