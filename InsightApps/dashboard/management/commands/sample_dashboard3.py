import json
from django.core.management.base import BaseCommand
from dashboard import models
import datetime
from django.core.files.uploadedfile import InMemoryUploadedFile
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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-Corona Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)  # Load JSON data from the text file

        # Get current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

        # Define the output file name
        queryset_file_name = f"sample_corona_queryset_{current_datetime}.txt"
        # S3 key for the output file
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
            # "file_id": "",
            "table_names": [['main', 'covid_data', 'covid_data']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": """SELECT \"covid_data\".\"country\" AS \"country\", 
                                    \"covid_data\".\"continent\" AS \"continent\", 
                                    \"covid_data\".\"population\" AS \"population\", 
                                    \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                    \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                    \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                    \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                    \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                    \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                    \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                    \"covid_data\".\"serious\" AS \"serious\", 
                                    \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                    \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                    \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                    \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                    \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                FROM \"main\".\"covid_data\" AS \"covid_data\"
                            """,
            "query_name": "Global Corona Data",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "datasource_path": queryset_file_key,
            "datasource_json": queryset_file_url
        }

        # Convert lists and other non-string data to JSON strings
        querySetDefaultData['table_names'] = json.dumps(
            querySetDefaultData['table_names'])
        querySetDefaultData['join_type'] = json.dumps(
            querySetDefaultData['join_type'])
        querySetDefaultData['joining_conditions'] = json.dumps(
            querySetDefaultData['joining_conditions'])

        # Create and save the QuerySets instance
        query_set_instance = models.QuerySets(
            user_id=querySetDefaultData["user_id"],
            server_id=querySetDefaultData["server_id"],
            # file_id=querySetDefaultData["file_id"],
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
        querysetid = models.QuerySets.objects.get(
            user_id=user_id, queryset_id=query_set_instance.queryset_id)
        self.stdout.write(self.style.SUCCESS(
            'Successfully imported data into QuerySet'))

        # print(" ##########\n Sample 1",querysetid.queryset_id)
        # chartFiltersData= [
        #     {
        #         "user_id": user_id,
        #         "server_id": server_id,
        #         # "file_id": "",
        #         "datasource_querysetid": "",
        #         "queryset_id": querysetid.queryset_id,
        #         "col_name": "gender",
        #         "data_type": "varchar",
        #         "filter_data": "('Female',)",
        #         "row_data": "('Female', 'Male')",
        #         "format_type": "%m/%d/%Y",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "server_id": server_id,
        #         # "file_id": "",
        #         "datasource_querysetid": "",
        #         "queryset_id": querysetid.queryset_id,
        #         "col_name": "gender",
        #         "data_type": "varchar",
        #         "filter_data": "('Male',)",
        #         "row_data": "('Female', 'Male')",
        #         "format_type": "%m/%d/%Y",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     }
        # ]
        # try:
        #     for filter_data in chartFiltersData:
        #         models.ChartFilters.objects.create(
        #             user_id=filter_data["user_id"],
        #             server_id=filter_data["server_id"] or None,
        #             # file_id=filter_data["file_id"] or None,
        #             datasource_querysetid=filter_data["datasource_querysetid"] or None,
        #             queryset_id=filter_data["queryset_id"] or None,
        #             col_name=filter_data["col_name"],
        #             data_type=filter_data["data_type"],
        #             filter_data=filter_data["filter_data"],
        #             row_data=filter_data["row_data"],
        #             format_type=filter_data["format_type"],
        #             created_at=datetime.datetime.now(),
        #             updated_at=datetime.datetime.now(),
        #         )
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Chart Filter'))
        # except Exception as e:
        #     pass

        # filter_id1 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[0]
        # filter_id2 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id',flat=True)[1]

        sheetFilterQuerySetData = [
            {
                # Total Cases
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(total_cases)"'],
                "custom_query": """SELECT SUM(\"total_cases\") AS \"sum(total_cases)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Population
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(population)"'],
                "custom_query": """SELECT SUM(\"population\") AS \"sum(population)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Active Cases
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(active_cases)"'],
                "custom_query": """SELECT SUM(\"active_cases\") AS \"sum(active_cases)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                            FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Recovered
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(total_recovered)"'],
                "custom_query": """SELECT SUM(\"total_recovered\") AS \"sum(total_recovered)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Deaths
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(total_deaths)"'],
                "custom_query": """SELECT SUM(\"total_deaths\") AS \"sum(total_deaths)\" 
                                        FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                    \"covid_data\".\"continent\" AS \"continent\", 
                                                    \"covid_data\".\"population\" AS \"population\", 
                                                    \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                    \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                    \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                    \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                    \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                    \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                    \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                    \"covid_data\".\"serious\" AS \"serious\", 
                                                    \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                    \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                    \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                    \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                    \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                            FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table
                                        """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Region Wise Total Cases per One Million Population
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "WHO region"'],
                "rows": ['"Total Cases per one Million Pop"', '"Tot deaths by One Million Pop"'],
                "custom_query": """SELECT \"WHO region\" AS \"WHO region\", 
                                        SUM(\"Tot cases/1M pop\") AS \"Total Cases per one Million Pop\", 
                                        SUM(\"Deaths/1M pop\") AS \"Tot deaths by One Million Pop\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                    GROUP BY \"WHO region\", \"WHO region\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Country wise Critical condition cases
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "country"'],
                "rows": ['"sum(serious)"'],
                "custom_query": """SELECT \"country\" AS \"country\", 
                                        SUM(\"serious\") AS \"sum(serious)\" 
                                        FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                    \"covid_data\".\"continent\" AS \"continent\", 
                                                    \"covid_data\".\"population\" AS \"population\", 
                                                    \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                    \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                    \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                    \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                    \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                    \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                    \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                    \"covid_data\".\"serious\" AS \"serious\", 
                                                    \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                    \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                    \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                    \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                    \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                            FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                        GROUP BY \"country\", \"country\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Region Wise Tests Performed
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "WHO region"'],
                "rows": ['"sum(total_tests)"'],
                "custom_query": """SELECT \"WHO region\" AS \"WHO region\", 
                                    SUM(\"total_tests\") AS \"sum(total_tests)\" 
                                FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                            \"covid_data\".\"continent\" AS \"continent\", 
                                            \"covid_data\".\"population\" AS \"population\", 
                                            \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                            \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                            \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                            \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                            \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                            \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                            \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                            \"covid_data\".\"serious\" AS \"serious\", 
                                            \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                            \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                            \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                            \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                            \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                    FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                GROUP BY \"WHO region\", \"WHO region\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Continent wise tests Per One Million Population
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "continent"'],
                "rows": ['"sum(Tests/1M pop)"'],
                "custom_query": """SELECT \"continent\" AS \"continent\", 
                                    SUM(\"Tests/1M pop\") AS \"sum(Tests/1M pop)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                    GROUP BY \"continent\", \"continent\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            
            {
                # Region Wise Active Cases & Critical Cases
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "WHO region"'],
                "rows": ['"active cases"', '"critical cases"'],
                "custom_query": """SELECT \"WHO region\" AS \"WHO region\", 
                                        SUM(\"active_cases\") AS \"active cases\", 
                                        SUM(\"serious\") AS \"critical cases\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                    GROUP BY \"WHO region\", \"WHO region\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Continent Wise Total Deaths
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "continent"'],
                "rows": ['"sum(total_deaths)"'],
                "custom_query": """SELECT \"continent\" AS \"continent\", 
                                        SUM(\"total_deaths\") AS \"sum(total_deaths)\" 
                                    FROM (SELECT \"covid_data\".\"country\" AS \"country\", 
                                                \"covid_data\".\"continent\" AS \"continent\", 
                                                \"covid_data\".\"population\" AS \"population\", 
                                                \"covid_data\".\"total_cases\" AS \"total_cases\", 
                                                \"covid_data\".\"new_cases\" AS \"new_cases\", 
                                                \"covid_data\".\"total_deaths\" AS \"total_deaths\", 
                                                \"covid_data\".\"new_deaths\" AS \"new_deaths\", 
                                                \"covid_data\".\"total_recovered\" AS \"total_recovered\", 
                                                \"covid_data\".\"new_recovered\" AS \"new_recovered\", 
                                                \"covid_data\".\"active_cases\" AS \"active_cases\", 
                                                \"covid_data\".\"serious\" AS \"serious\", 
                                                \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", 
                                                \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", 
                                                \"covid_data\".\"total_tests\" AS \"total_tests\", 
                                                \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", 
                                                \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                        FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                    GROUP BY \"continent\", \"continent\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Corona Cases Overview
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "server_id": server_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [' "country"', ' "continent"', ' "WHO region"', ' "population"', ' "total_tests"', ' "total_cases"', ' "total_deaths"', ' "total_recovered"', ' "active_cases"', ' "serious"'],
                "rows": [],
                "custom_query": """
                                SELECT \"country\" AS \"country\", \"continent\" AS \"continent\", \"WHO region\" AS \"WHO region\", \"population\" AS \"population\", \"total_tests\" AS \"total_tests\", \"total_cases\" AS \"total_cases\", \"total_deaths\" AS \"total_deaths\", \"total_recovered\" AS \"total_recovered\", \"active_cases\" AS \"active_cases\", \"serious\" AS \"serious\" 
                                FROM (SELECT \"covid_data\".\"country\" AS \"country\", \"covid_data\".\"continent\" AS \"continent\", \"covid_data\".\"population\" AS \"population\", \"covid_data\".\"total_cases\" AS \"total_cases\", \"covid_data\".\"new_cases\" AS \"new_cases\", \"covid_data\".\"total_deaths\" AS \"total_deaths\", \"covid_data\".\"new_deaths\" AS \"new_deaths\", \"covid_data\".\"total_recovered\" AS \"total_recovered\", \"covid_data\".\"new_recovered\" AS \"new_recovered\", \"covid_data\".\"active_cases\" AS \"active_cases\", \"covid_data\".\"serious\" AS \"serious\", \"covid_data\".\"Tot cases/1M pop\" AS \"Tot cases/1M pop\", \"covid_data\".\"Deaths/1M pop\" AS \"Deaths/1M pop\", \"covid_data\".\"total_tests\" AS \"total_tests\", \"covid_data\".\"Tests/1M pop\" AS \"Tests/1M pop\", \"covid_data\".\"WHO region\" AS \"WHO region\" 
                                FROM \"main\".\"covid_data\" AS \"covid_data\") temp_table 
                                GROUP BY \"country\", \"continent\", \"WHO region\", \"population\", \"total_tests\", \"total_cases\", \"total_deaths\", \"total_recovered\", \"active_cases\", \"serious\", \"country\", \"continent\", \"WHO region\", \"population\", \"total_tests\", \"total_cases\", \"total_deaths\", \"total_recovered\", \"active_cases\", \"serious\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },  
        ]
        try:
            for entry in sheetFilterQuerySetData:
                # Create a new SheetFilter_querysets object
                models.SheetFilter_querysets.objects.create(
                    datasource_querysetid=int(entry.get("datasource_querysetid") or 0) if entry.get(
                        "datasource_querysetid") else None,
                    queryset_id=int(entry.get("queryset_id") or 0) if entry.get(
                        "queryset_id") else None,
                    user_id=entry.get("user_id"),
                    server_id=int(entry.get("server_id") or 0) if entry.get(
                        "server_id") else None,
                    # file_id=int(entry.get("file_id") or 0) if entry.get("file_id") else None,
                    filter_id_list=json.dumps(entry.get("filter_id_list", [])),
                    columns=json.dumps(entry.get("columns", [])),
                    rows=json.dumps(entry.get("rows", [])),
                    custom_query=entry.get("custom_query"),
                    created_at=entry.get(
                        "created_at", datetime.datetime.now()),
                    updated_at=entry.get(
                        "updated_at", datetime.datetime.now()),
                )
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported data into SheetFilter QuerySet'))
        except Exception as e:
            pass

        sheet_filter_querysets = models.SheetFilter_querysets.objects.filter(
            user_id=user_id, queryset_id=querysetid.queryset_id).values_list('Sheetqueryset_id', flat=True)
        sheetData = [
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Cases",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.1-Total Cases.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Cases</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Population",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.2-Total Population.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Population</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Active Cases",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.3-Active Cases.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><strong>Active Cases</strong></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Recovered",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.4-Total Recovered.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Recovered</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Deaths",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.5-Total Deaths.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><strong>Total Deaths</strong></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 4,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Region Wise Total Cases per One Million Population",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.6-Region Wise Total Cases per One Million Population.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Region Wise Total Cases per One Million Population</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 29,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Country Wise Critical Condition Cases",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.7-Country Wise Critical Condition Cases.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Country Wise Critical Condition Cases</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 24,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Region Wise Tests Performed",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.8-Region Wise Tests Performed.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Region Wise Tests Performed</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 27,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Continent Wise Tests Per One Million Population",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.9-Continent Wise Tests Per One Million Population.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Continent Wise Tests Per One Million Population</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 8,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Region Wise Active Cases & Critical Cases",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.10-Region Wise Active Cases & Critical Cases.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Region Wise Active Cases & Critical Cases</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 10,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Continent Wise Total Deaths",
                "sheetfilter_querysets_id": sheet_filter_querysets[10],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.11-Continent Wise Total Deaths.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><strong>Continent Wise Total Deaths</strong></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 1,
                "server_id": server_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Overview of Corona Cases",
                "sheetfilter_querysets_id": sheet_filter_querysets[11],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '3.12-Overview of Corona Cases.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Overview of Corona Cases</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
        ]

        try:
            for data in sheetData:
                # Convert lists to JSON strings
                data['filter_ids'] = json.dumps(data['filter_ids'])

                # Upload the file to S3
                local_file_path = data['datapath']  # Local file path
                s3_url, file_key = upload_sheetdata_file_to_s3(
                    local_file_path, settings.AWS_STORAGE_BUCKET_NAME, data['sheetfilter_querysets_id'])

                # Update datasrc with the new S3 URL
                if s3_url:
                    data['datasrc'] = s3_url
                    data['datapath'] = file_key

                # Create and save the sheet_data instance
                sheet_data_instance = models.sheet_data(
                    user_id=data['user_id'],
                    chart_id=data['chart_id'],
                    server_id=data['server_id'],
                    # file_id=data['file_id'],
                    is_sample=True,
                    queryset_id=data['queryset_id'],
                    filter_ids=data['filter_ids'],
                    sheet_name=data['sheet_name'],
                    sheet_filt_id=data['sheetfilter_querysets_id'],
                    # Assuming the file already exists in the given path
                    datapath=data['datapath'],
                    datasrc=data['datasrc'],
                    sheet_tag_name=data['sheet_tag_name'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                )

                sheet_data_instance.save()
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported data into Sheet Data'))
        except Exception as e:
            pass

        sheet_ids_list = list(models.sheet_data.objects.filter(
            user_id=user_id, queryset_id=querysetid.queryset_id).values_list('id', flat=True))

        try:
            # Define the path to the input JSON text file
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard',
                                           'Dashboard-Global Corona Dashboard.txt')  # Replace with your actual .txt file name

            # Read the JSON data from the .txt file
            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)  # Load JSON data from the text file

            # Update the sheetId in the data
            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = server_id
                item['qrySetId'] = querysetid.queryset_id

            # Upload the JSON file to S3
            file_url, output_file_key = create_s3_file(
                input_file_path, sheet_ids_list, server_id, querysetid, settings.AWS_STORAGE_BUCKET_NAME)
            # file_url = self.create_s3_file(data=json_data, file_name=output_file_key, bucket_name=settings.AWS_STORAGE_BUCKET_NAME)

            # Define the path to the input image file
            image_image_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands',
                                            'dashboard', 'images', '2024-11-04_12_20_37.3217051730703018268.jpeg')

            # Get current date and time
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

            # Upload the image to S3
            image_url, output_image_key = create_s3_image(
                image_image_path, current_datetime, settings.AWS_STORAGE_BUCKET_NAME)
            # image_url = self.create_s3_image(image_path = image_file_path, image_name = output_image_key, bucket_name=settings.AWS_STORAGE_BUCKET_NAME)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return Response({"message": str(e)}, status=400)

        dashboardSampleData = {
            "user_id": user_id,
            "server_id": [server_id],
            "queryset_id": [querysetid.queryset_id],
            # "file_id": "",
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "2180",
            "width": "900",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "Global Covid Analysis Dashboard",
            "datapath": output_file_key,  # Update with the new S3 file key
            "datasrc": file_url,  # Update with the new S3 file URL
            "imagepath": output_image_key,  # Update with the new S3 image key
            "imagesrc": image_url,  # Update with the new S3 image URL
            "dashboard_tag_name": """<p style="text-align:center;"><span style="font-size:16px;"><strong>Global Covid Analysis Dashboard</strong></span></p>""",
            "is_public": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        try:
            dashboard_data_instance = models.dashboard_data(
                user_id=dashboardSampleData["user_id"],
                server_id=dashboardSampleData["server_id"] or None,
                queryset_id=dashboardSampleData["queryset_id"] or None,
                # file_id=dashboardSampleData["file_id"] or None,
                sheet_ids=','.join(map(str, dashboardSampleData["sheet_ids"])),
                selected_sheet_ids=','.join(
                    map(str, dashboardSampleData["selected_sheet_ids"])),
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
            # dashboard = models.dashboard_data.objects.get(user_id=user_id,queryset_id=querysetid.queryset_id)
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported data into Dashbaord Data'))
        except Exception as e:
            pass

        dashbaordFiltersSampleData=[
                {
                    "user_id": user_id,
                    "dashboard_id": dashboard_data_instance.id,
                    "sheet_id_list": sheet_ids_list,
                    "filter_name": "Region",
                    "table_name" : "covid_data",
                    "column_name": "WHO region",
                    "column_datatype": "string",
                    "queryset_id": querysetid.queryset_id,
                    "created_at":datetime.datetime.now(),
                    "updated_at":datetime.datetime.now()
                },
                # {
                #     "user_id": user_id,
                #     "dashboard_id": dashboard_data_instance.id,
                #     "sheet_id_list": sheet_ids_list[4:],
                #     "filter_name": "Department",
                #     "table_name" : "employees",
                #     "column_name": "department",
                #     "column_datatype": "string",
                #     "queryset_id": querysetid.queryset_id,
                # "created_at":datetime.datetime.now(),
                # "updated_at":datetime.datetime.now()
                # },
                # {
                #     "user_id": user_id,
                #     "dashboard_id": dashboard_data_instance.id,
                #     "sheet_id_list": sheet_ids_list[4:],
                #     "filter_name": "Gender",
                #     "table_name" : "employees",
                #     "column_name": "gender",
                #     "column_datatype": "string",
                #     "queryset_id": querysetid.queryset_id,
                # "created_at":datetime.datetime.now(),
                # "updated_at":datetime.datetime.now()
                # }
            ]
        try:
            for filter_data in dashbaordFiltersSampleData:
                models.DashboardFilters.objects.create(
                    user_id=filter_data["user_id"],
                    dashboard_id=filter_data["dashboard_id"],
                    sheet_id_list=','.join(map(str, filter_data["sheet_id_list"])),
                    filter_name=filter_data["filter_name"],
                    table_name= filter_data["table_name"],
                    column_name=filter_data["column_name"],
                    column_datatype=filter_data["column_datatype"],
                    queryset_id=filter_data["queryset_id"] or None,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashbaord Filter Data'))
        except Exception as e:
            pass
