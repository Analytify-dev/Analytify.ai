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
        parser.add_argument('hierarchy_id', type=int, help='Server ID for the operation')

    def handle(self, *args, **options):
        user_id = options['user_id']  # Retrieve user_id from options
        hierarchy_id = options['hierarchy_id']  # Retrieve server_id from options

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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-Sales Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)  # Load JSON data from the text file

        # Get current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

        # Define the output file name
        queryset_file_name = f"sample_salesdata_queryset_{current_datetime}.txt"
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
            "hierarchy_id": hierarchy_id,
            # "file_id": "",
            "table_names": [['In Ex', 'sales', 'sales']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": """
                            SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                \"sales\".\"price_each\" AS \"price_each\", 
                                \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                \"sales\".\"sales\" AS \"sales\", 
                                \"sales\".\"order_Date\" AS \"order_Date\", 
                                \"sales\".\"status\" AS \"status\", 
                                \"sales\".\"month_id\" AS \"month_id\", 
                                \"sales\".\"Year_id\" AS \"Year_id\", 
                                \"sales\".\"product_line\" AS \"product_line\", 
                                \"sales\".\"MSRP\" AS \"MSRP\", 
                                \"sales\".\"product_code\" AS \"product_code\", 
                                \"sales\".\"customer_name\" AS \"customer_name\", 
                                \"sales\".\"phone_number\" AS \"phone_number\", 
                                \"sales\".\"address_1\" AS \"address_1\", 
                                \"sales\".\"address_2\" AS \"address_2\", 
                                \"sales\".\"City\" AS \"City\", 
                                \"sales\".\"state\" AS \"state\", 
                                \"sales\".\"postal_code\" AS \"postal_code\", 
                                \"sales\".\"country\" AS \"country\", 
                                \"sales\".\"Territory\" AS \"Territory\", 
                                \"sales\".\"lastname\" AS \"lastname\", 
                                \"sales\".\"firstname\" AS \"firstname\", 
                                \"sales\".\"deal_size\" AS \"deal_size\" 
                            FROM \"In Ex\".\"sales\" AS \"sales\"
                            """,
            "query_name": "Sales Data",
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
            hierarchy_id=querySetDefaultData["hierarchy_id"],
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

        # chartFiltersData= [
        #     {
        #         "user_id": user_id,
        #         "hierarchy_id": hierarchy_id,
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
        #         "hierarchy_id": hierarchy_id,
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
                # Total Customers
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"CNTD(customer_name)"'],
                "custom_query": """
                                SELECT COUNT(DISTINCT \"customer_name\") AS \"CNTD(customer_name)\" 
                                    FROM (
                                        SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                            \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"sales\".\"price_each\" AS \"price_each\", 
                                            \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                            \"sales\".\"sales\" AS \"sales\", 
                                            \"sales\".\"order_Date\" AS \"order_Date\", 
                                            \"sales\".\"status\" AS \"status\", 
                                            \"sales\".\"month_id\" AS \"month_id\", 
                                            \"sales\".\"Year_id\" AS \"Year_id\", 
                                            \"sales\".\"product_line\" AS \"product_line\", 
                                            \"sales\".\"MSRP\" AS \"MSRP\", 
                                            \"sales\".\"product_code\" AS \"product_code\", 
                                            \"sales\".\"customer_name\" AS \"customer_name\", 
                                            \"sales\".\"phone_number\" AS \"phone_number\", 
                                            \"sales\".\"address_1\" AS \"address_1\", 
                                            \"sales\".\"address_2\" AS \"address_2\", 
                                            \"sales\".\"City\" AS \"City\", 
                                            \"sales\".\"state\" AS \"state\", 
                                            \"sales\".\"postal_code\" AS \"postal_code\", 
                                            \"sales\".\"country\" AS \"country\", 
                                            \"sales\".\"Territory\" AS \"Territory\", 
                                            \"sales\".\"lastname\" AS \"lastname\", 
                                            \"sales\".\"firstname\" AS \"firstname\", 
                                            \"sales\".\"deal_size\" AS \"deal_size\" 
                                        FROM \"In Ex\".\"sales\" AS \"sales\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Orders
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"count(order_number)"'],
                "custom_query": """
                                    SELECT COUNT(\"order_number\") AS \"count(order_number)\" 
                                    FROM (
                                        SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                            \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"sales\".\"price_each\" AS \"price_each\", 
                                            \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                            \"sales\".\"sales\" AS \"sales\", 
                                            \"sales\".\"order_Date\" AS \"order_Date\", 
                                            \"sales\".\"status\" AS \"status\", 
                                            \"sales\".\"month_id\" AS \"month_id\", 
                                            \"sales\".\"Year_id\" AS \"Year_id\", 
                                            \"sales\".\"product_line\" AS \"product_line\", 
                                            \"sales\".\"MSRP\" AS \"MSRP\", 
                                            \"sales\".\"product_code\" AS \"product_code\", 
                                            \"sales\".\"customer_name\" AS \"customer_name\", 
                                            \"sales\".\"phone_number\" AS \"phone_number\", 
                                            \"sales\".\"address_1\" AS \"address_1\", 
                                            \"sales\".\"address_2\" AS \"address_2\", 
                                            \"sales\".\"City\" AS \"City\", 
                                            \"sales\".\"state\" AS \"state\", 
                                            \"sales\".\"postal_code\" AS \"postal_code\", 
                                            \"sales\".\"country\" AS \"country\", 
                                            \"sales\".\"Territory\" AS \"Territory\", 
                                            \"sales\".\"lastname\" AS \"lastname\", 
                                            \"sales\".\"firstname\" AS \"firstname\", 
                                            \"sales\".\"deal_size\" AS \"deal_size\" 
                                        FROM \"In Ex\".\"sales\" AS \"sales\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Products
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"CNTD(product_line)"'],
                "custom_query": """SELECT COUNT(DISTINCT \"product_line\") AS \"CNTD(product_line)\" 
                                    FROM (
                                        SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                            \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"sales\".\"price_each\" AS \"price_each\", 
                                            \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                            \"sales\".\"sales\" AS \"sales\", 
                                            \"sales\".\"order_Date\" AS \"order_Date\", 
                                            \"sales\".\"status\" AS \"status\", 
                                            \"sales\".\"month_id\" AS \"month_id\", 
                                            \"sales\".\"Year_id\" AS \"Year_id\", 
                                            \"sales\".\"product_line\" AS \"product_line\", 
                                            \"sales\".\"MSRP\" AS \"MSRP\", 
                                            \"sales\".\"product_code\" AS \"product_code\", 
                                            \"sales\".\"customer_name\" AS \"customer_name\", 
                                            \"sales\".\"phone_number\" AS \"phone_number\", 
                                            \"sales\".\"address_1\" AS \"address_1\", 
                                            \"sales\".\"address_2\" AS \"address_2\", 
                                            \"sales\".\"City\" AS \"City\", 
                                            \"sales\".\"state\" AS \"state\", 
                                            \"sales\".\"postal_code\" AS \"postal_code\", 
                                            \"sales\".\"country\" AS \"country\", 
                                            \"sales\".\"Territory\" AS \"Territory\", 
                                            \"sales\".\"lastname\" AS \"lastname\", 
                                            \"sales\".\"firstname\" AS \"firstname\", 
                                            \"sales\".\"deal_size\" AS \"deal_size\" 
                                        FROM \"In Ex\".\"sales\" AS \"sales\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Sales
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(sales)"'],
                "custom_query": """SELECT SUM(\"sales\") AS \"sum(sales)\" 
                                    FROM (
                                        SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                            \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"sales\".\"price_each\" AS \"price_each\", 
                                            \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                            \"sales\".\"sales\" AS \"sales\", 
                                            \"sales\".\"order_Date\" AS \"order_Date\", 
                                            \"sales\".\"status\" AS \"status\", 
                                            \"sales\".\"month_id\" AS \"month_id\", 
                                            \"sales\".\"Year_id\" AS \"Year_id\", 
                                            \"sales\".\"product_line\" AS \"product_line\", 
                                            \"sales\".\"MSRP\" AS \"MSRP\", 
                                            \"sales\".\"product_code\" AS \"product_code\", 
                                            \"sales\".\"customer_name\" AS \"customer_name\", 
                                            \"sales\".\"phone_number\" AS \"phone_number\", 
                                            \"sales\".\"address_1\" AS \"address_1\", 
                                            \"sales\".\"address_2\" AS \"address_2\", 
                                            \"sales\".\"City\" AS \"City\", 
                                            \"sales\".\"state\" AS \"state\", 
                                            \"sales\".\"postal_code\" AS \"postal_code\", 
                                            \"sales\".\"country\" AS \"country\", 
                                            \"sales\".\"Territory\" AS \"Territory\", 
                                            \"sales\".\"lastname\" AS \"lastname\", 
                                            \"sales\".\"firstname\" AS \"firstname\", 
                                            \"sales\".\"deal_size\" AS \"deal_size\" 
                                        FROM \"In Ex\".\"sales\" AS \"sales\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Total Quantity Ordered
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(quantity_ordered)"'],
                "custom_query": """SELECT SUM(\"quantity_ordered\") AS \"sum(quantity_ordered)\" 
                                    FROM (
                                        SELECT \"sales\".\"order_number\" AS \"order_number\", 
                                            \"sales\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"sales\".\"price_each\" AS \"price_each\", 
                                            \"sales\".\"order_line_number\" AS \"order_line_number\", 
                                            \"sales\".\"sales\" AS \"sales\", 
                                            \"sales\".\"order_Date\" AS \"order_Date\", 
                                            \"sales\".\"status\" AS \"status\", 
                                            \"sales\".\"month_id\" AS \"month_id\", 
                                            \"sales\".\"Year_id\" AS \"Year_id\", 
                                            \"sales\".\"product_line\" AS \"product_line\", 
                                            \"sales\".\"MSRP\" AS \"MSRP\", 
                                            \"sales\".\"product_code\" AS \"product_code\", 
                                            \"sales\".\"customer_name\" AS \"customer_name\", 
                                            \"sales\".\"phone_number\" AS \"phone_number\", 
                                            \"sales\".\"address_1\" AS \"address_1\", 
                                            \"sales\".\"address_2\" AS \"address_2\", 
                                            \"sales\".\"City\" AS \"City\", 
                                            \"sales\".\"state\" AS \"state\", 
                                            \"sales\".\"postal_code\" AS \"postal_code\", 
                                            \"sales\".\"country\" AS \"country\", 
                                            \"sales\".\"Territory\" AS \"Territory\", 
                                            \"sales\".\"lastname\" AS \"lastname\", 
                                            \"sales\".\"firstname\" AS \"firstname\", 
                                            \"sales\".\"deal_size\" AS \"deal_size\" 
                                        FROM \"In Ex\".\"sales\" AS \"sales\"
                                    ) temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Year wise Sales Drill down
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"year(order_Date)"'],
                "rows": ['"sum(sales)"'],
                "custom_query": """
                                    SELECT 
                                        DATE_FORMAT(CAST("order_Date" AS TIMESTAMP), '%Y') AS "year(order_Date)", 
                                        SUM("sales") AS "sum(sales)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "year(order_Date)"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Product Wise Quantity Ordered
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"product_line"'],
                "rows": ['"sum(quantity_ordered)"'],
                "custom_query": """
                                    SELECT 
                                        "product_line" AS "product_line", 
                                        SUM("quantity_ordered") AS "sum(quantity_ordered)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "product_line"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Status Wise Orders
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"status"'],
                "rows": ['"count(order_number)"'],
                "custom_query": """
                                    SELECT 
                                        "status" AS "status", 
                                        COUNT("order_number") AS "count(order_number)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "status"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Sales By Deal Size
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"deal_size"'],
                "rows": ['"sum(sales)"'],
                "custom_query": """
                                    SELECT 
                                        "deal_size" AS "deal_size", 
                                        SUM("sales") AS "sum(sales)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "deal_size"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            
            {
                # Product Wise Price and Manufacture Suggested Retail Price
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"product_line"'],
                "rows": ['"sum(price_each)"', '"sum(MSRP)"'],
                "custom_query": """
                                    SELECT 
                                        "product_line" AS "product_line", 
                                        SUM("price_each") AS "sum(price_each)", 
                                        SUM("MSRP") AS "sum(MSRP)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "product_line"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Country Wise Sales
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"country"'],
                "rows": ['"sum(sales)"'],
                "custom_query": """SELECT 
                                        "country" AS "country", 
                                        SUM("sales") AS "sum(sales)" 
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) AS temp_table 
                                    GROUP BY "country"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                # Customer Wise Sales Overview
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "filter_id_list": [],
                "columns": ['"customer_name"', '"product_line"', '"product_code"', '"order_number"', '"quantity_ordered"', '"sales"'],
                "rows": [],
                "custom_query": """
                                    SELECT 
                                        "customer_name" AS "customer_name",
                                        "product_line" AS "product_line",
                                        "product_code" AS "product_code",
                                        "order_number" AS "order_number",
                                        "quantity_ordered" AS "quantity_ordered",
                                        "sales" AS "sales"
                                    FROM (
                                        SELECT 
                                            "sales"."order_number" AS "order_number", 
                                            "sales"."quantity_ordered" AS "quantity_ordered", 
                                            "sales"."price_each" AS "price_each", 
                                            "sales"."order_line_number" AS "order_line_number", 
                                            "sales"."sales" AS "sales", 
                                            "sales"."order_Date" AS "order_Date", 
                                            "sales"."status" AS "status", 
                                            "sales"."month_id" AS "month_id", 
                                            "sales"."Year_id" AS "Year_id", 
                                            "sales"."product_line" AS "product_line", 
                                            "sales"."MSRP" AS "MSRP", 
                                            "sales"."product_code" AS "product_code", 
                                            "sales"."customer_name" AS "customer_name", 
                                            "sales"."phone_number" AS "phone_number", 
                                            "sales"."address_1" AS "address_1", 
                                            "sales"."address_2" AS "address_2", 
                                            "sales"."City" AS "City", 
                                            "sales"."state" AS "state", 
                                            "sales"."postal_code" AS "postal_code", 
                                            "sales"."country" AS "country", 
                                            "sales"."Territory" AS "Territory", 
                                            "sales"."lastname" AS "lastname", 
                                            "sales"."firstname" AS "firstname", 
                                            "sales"."deal_size" AS "deal_size" 
                                        FROM "In Ex"."sales" AS "sales"
                                    ) temp_table 
                                    GROUP BY 
                                        "customer_name", 
                                        "product_line", 
                                        "product_code", 
                                        "order_number", 
                                        "quantity_ordered", 
                                        "sales"
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
                    hierarchy_id=int(entry.get("hierarchy_id") or 0) if entry.get(
                        "hierarchy_id") else None,
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
            self.stdout.write(self.style.ERROR(
                f'SheetFilter Queryset Error {e}'))
            return Response(e)

        sheet_filter_querysets = models.SheetFilter_querysets.objects.filter(
            user_id=user_id, queryset_id=querysetid.queryset_id).values_list('Sheetqueryset_id', flat=True)
        sheetData = [
            # Total Customers
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Customers",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.1-Total Customers.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Customers</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Orders
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Orders",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.2-Total Orders.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Orders</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Products
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Products",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.3-Total Products.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Products</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Sales
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Sales",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.4-Total Sales.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Sales</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Quantity Ordered
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Quantity Ordered",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.5-Total Quantity Ordered.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Quantity Ordered</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Year wise Sales Drill down
            {
                "user_id": user_id,
                "chart_id": 6,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Year Wise sales Drill down",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.6-Year Wise sales Drill down.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Year Wise sales Drill down</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Product Wise Quantity Ordered
            {
                "user_id": user_id,
                "chart_id": 26,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Product Wise Quantity Ordered",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.7-Product Wise Quantity Ordered.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Product Wise Quantity Ordered</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Status Wise Orders
            {
                "user_id": user_id,
                "chart_id": 24,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Status Wise Orders",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.8-Status Wise Orders.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Status Wise Orders</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Sales By Deal Size
            {
                "user_id": user_id,
                "chart_id": 10,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Sales By Deal Sizen",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.9-Sales By Deal Size.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Sales By Deal Size</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Product Wise Price and Manufacture Suggested Retail Price
            {
                "user_id": user_id,
                "chart_id": 12,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Product Wise Price and Manufacture Suggested Retail Price",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.10-Product Wise Price and Manufacture Suggested Retail Price.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Product Wise Price and Manufacture Suggested Retail Price</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Country Wise Sales
            {
                "user_id": user_id,
                "chart_id": 29,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Country Wise Sales",
                "sheetfilter_querysets_id": sheet_filter_querysets[10],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.11-Country Wise Sales.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><strong>Country Wise Sales</strong></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Customer Wise Sales Overview
            {
                "user_id": user_id,
                "chart_id": 1,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Customer Wise Sales Overview",
                "sheetfilter_querysets_id": sheet_filter_querysets[11],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '4.12-Customer Wise Sales Overview.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Customer Wise Sales Overview</strong></span></p>""",
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

                # Create and save the sheet_data instance
                sheet_data_instance = models.sheet_data(
                    user_id=data['user_id'],
                    chart_id=data['chart_id'],
                    hierarchy_id=data['hierarchy_id'],
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
            self.stdout.write(self.style.ERROR(
                f'Sheet Data Error {e}'))
            return Response(e)
            # pass

        sheet_ids_list = list(models.sheet_data.objects.filter(
            user_id=user_id, queryset_id=querysetid.queryset_id).values_list('id', flat=True).order_by('id'))

        try:
            input_file_name = 'Dashboard-Sales Data.txt'
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
                media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'dashboard')
                os.makedirs(media_path, exist_ok=True)
                local_path = os.path.join(media_path, input_file_name)
                with open(local_path, 'w') as f:
                    json.dump(data, f, indent=4)
                file_url = f"{settings.file_save_url.rstrip('/')}/media/insightapps/dashboard/{input_file_name}"
                output_file_key = local_path

            image_file_name = 'SalesDashboardImage.jpeg'
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
            "hierarchy_id": [hierarchy_id],
            "queryset_id": [querysetid.queryset_id],
            # "file_id": "",
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "2200",
            "width": "800",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "Sales Analysis Dashboard",
            "datapath": output_file_key,  # Update with the new S3 file key
            "datasrc": file_url,  # Update with the new S3 file URL
            "imagepath": output_image_key,  # Update with the new S3 image key
            "imagesrc": image_url,  # Update with the new S3 image URL
            "dashboard_tag_name": """<p style="text-align:center;"><span style="font-size:16px;"><strong>Sales Analysis Dashboard</strong></span></p>""",
            "is_public": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        }
        try:
            dashboard_data_instance = models.dashboard_data(
                user_id=dashboardSampleData["user_id"],
                hierarchy_id=dashboardSampleData["hierarchy_id"] or None,
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
                    "filter_name": "Status",
                    "table_name" : "sales",
                    "column_name": "status",
                    "column_datatype": "string",
                    "hierarchy_id" : hierarchy_id,
                    "queryset_id": [querysetid.queryset_id],
                    "created_at":datetime.datetime.now(),
                    "updated_at":datetime.datetime.now()
                },
                {
                    "user_id": user_id,
                    "dashboard_id": dashboard_data_instance.id,
                    "sheet_id_list": sheet_ids_list,
                    "filter_name": "Country",
                    "table_name" : "sales",
                    "column_name": "country",
                    "column_datatype": "string",
                    "hierarchy_id" : hierarchy_id,
                    "queryset_id": [querysetid.queryset_id],
                    "created_at":datetime.datetime.now(),
                    "updated_at":datetime.datetime.now()
                },
                {
                    "user_id": user_id,
                    "dashboard_id": dashboard_data_instance.id,
                    "sheet_id_list": sheet_ids_list,
                    "filter_name": "Territory",
                    "table_name" : "sales",
                    "column_name": "Territory",
                    "column_datatype": "string",
                    "hierarchy_id" : hierarchy_id,
                    "queryset_id": [querysetid.queryset_id],
                    "created_at":datetime.datetime.now(),
                    "updated_at":datetime.datetime.now()
                }
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
                    hierarchy_id=filter_data["hierarchy_id"],
                    selected_query = querysetid.queryset_id,
                    queryset_id=filter_data["queryset_id"] or None,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )

            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashbaord Filter Data'))
        except Exception as e:
            pass
