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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-SupplyChain Data.txt'), 'r') as txt_file:
            data = json.load(txt_file)

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
        queryset_file_name = f"sample_supplychain_queryset_{current_datetime}.txt"
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
            "table_names": [['In Ex', 'supply_chain', 'supply_chain']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": "SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\"",
            "query_name": "Supply Chain Data",
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
        
        # chartFiltersData = [
        #     {
        #         "user_id": user_id,
        #         "hierarchy_id":hierarchy_id,
        #         "datasource_querysetid": "",
        #         "queryset_id": querysetid.queryset_id,
        #         "col_name": "gender",
        #         "data_type": "varchar",
        #         "filter_data": "('Female',)",
        #         "row_data": "('Female', 'Male')",
        #         "format_type": "%m/%d/%Y",
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "hierarchy_id":hierarchy_id,
        #         "datasource_querysetid": "",
        #         "queryset_id": querysetid.queryset_id,
        #         "col_name": "gender",
        #         "data_type": "varchar",
        #         "filter_data": "('Male',)",
        #         "row_data": "('Female', 'Male')",
        #         "format_type": "%m/%d/%Y",
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     }
        # ]
        # try:
        #     for filter_data in chartFiltersData:
        #         models.ChartFilters.objects.create(
        #             user_id=filter_data["user_id"],
        #             hierarchy_id=filter_data["hierarchy_id"] or None,
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
        
        # filter_id1 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[0]
        # filter_id2 = models.ChartFilters.objects.filter(queryset_id=querysetid.queryset_id).values_list('filter_id', flat=True)[1]
        
        sheetFilterQuerySetData = [
            # Total Orders
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id": hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": [' "CNTD(order_id)"'],
                "custom_query": """
                                SELECT COUNT(DISTINCT \"order_id\") AS \"CNTD(order_id)\" FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Suppliers
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": [' "CNTD(supplier_id)"'],
                "custom_query": """
                                SELECT COUNT(DISTINCT \"supplier_id\") AS \"CNTD(supplier_id)\" FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Total Products
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": [' "CNTD(product_id)"'],
                "custom_query": """
                                SELECT COUNT(DISTINCT \"product_id\") AS \"CNTD(product_id)\" FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table                                
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Quantity Ordered
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(quantity_ordered)"'],
                "custom_query": """ SELECT SUM(\"quantity_ordered\") AS \"sum(quantity_ordered)\" FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },     
            # Quantity Received           
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [],
                "rows": ['"sum(quantity_received)"'],
                "custom_query": """ SELECT SUM(\"quantity_received\") AS \"sum(quantity_received)\" FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", \"supply_chain\".\"order_date\" AS \"order_date\", \"supply_chain\".\"supplier_id\" AS \"supplier_id\", \"supply_chain\".\"supplier_name\" AS \"supplier_name\", \"supply_chain\".\"product_id\" AS \"product_id\", \"supply_chain\".\"product_name\" AS \"product_name\", \"supply_chain\".\"product_category\" AS \"product_category\", \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", \"supply_chain\".\"quantity_received\" AS \"quantity_received\", \"supply_chain\".\"order_status\" AS \"order_status\", \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", \"supply_chain\".\"total_cost\" AS \"total_cost\", \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", \"supply_chain\".\"inventory_level\" AS \"inventory_level\", \"supply_chain\".\"backorder_status\" AS \"backorder_status\", \"supply_chain\".\"delivery_date\" AS \"delivery_date\", \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", \"supply_chain\".\"order_comments\" AS \"order_comments\" FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },      
            # Total Cost By Order Date      
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"year(order_date)"'],
                "rows": ['"sum(total_cost)"'],
                "custom_query": """ SELECT DATE_FORMAT(CAST(\"order_date\" AS TIMESTAMP), '%Y') AS \"year(order_date)\", 
                                        SUM(\"total_cost\") AS \"sum(total_cost)\" 
                                    FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", 
                                                \"supply_chain\".\"order_date\" AS \"order_date\", 
                                                \"supply_chain\".\"supplier_id\" AS \"supplier_id\", 
                                                \"supply_chain\".\"supplier_name\" AS \"supplier_name\", 
                                                \"supply_chain\".\"product_id\" AS \"product_id\", 
                                                \"supply_chain\".\"product_name\" AS \"product_name\", 
                                                \"supply_chain\".\"product_category\" AS \"product_category\", 
                                                \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                                \"supply_chain\".\"quantity_received\" AS \"quantity_received\", 
                                                \"supply_chain\".\"order_status\" AS \"order_status\", 
                                                \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", 
                                                \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", 
                                                \"supply_chain\".\"total_cost\" AS \"total_cost\", 
                                                \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", 
                                                \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", 
                                                \"supply_chain\".\"inventory_level\" AS \"inventory_level\", 
                                                \"supply_chain\".\"backorder_status\" AS \"backorder_status\", 
                                                \"supply_chain\".\"delivery_date\" AS \"delivery_date\", 
                                                \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", 
                                                \"supply_chain\".\"order_comments\" AS \"order_comments\" 
                                        FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table 
                                    GROUP BY \"year(order_date)\" 
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Region Wise Quantity Ordered and Received
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"warehouse_location"'],
                "rows": ['"sum(quantity_ordered)"', '"sum(quantity_received)"'],
                "custom_query": """
                                SELECT \"warehouse_location\" AS \"warehouse_location\", 
                                    SUM(\"quantity_ordered\") AS \"sum(quantity_ordered)\", 
                                    SUM(\"quantity_received\") AS \"sum(quantity_received)\" 
                                FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", 
                                            \"supply_chain\".\"order_date\" AS \"order_date\", 
                                            \"supply_chain\".\"supplier_id\" AS \"supplier_id\", 
                                            \"supply_chain\".\"supplier_name\" AS \"supplier_name\", 
                                            \"supply_chain\".\"product_id\" AS \"product_id\", 
                                            \"supply_chain\".\"product_name\" AS \"product_name\", 
                                            \"supply_chain\".\"product_category\" AS \"product_category\", 
                                            \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"supply_chain\".\"quantity_received\" AS \"quantity_received\", 
                                            \"supply_chain\".\"order_status\" AS \"order_status\", 
                                            \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", 
                                            \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", 
                                            \"supply_chain\".\"total_cost\" AS \"total_cost\", 
                                            \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", 
                                            \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", 
                                            \"supply_chain\".\"inventory_level\" AS \"inventory_level\", 
                                            \"supply_chain\".\"backorder_status\" AS \"backorder_status\", 
                                            \"supply_chain\".\"delivery_date\" AS \"delivery_date\", 
                                            \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", 
                                            \"supply_chain\".\"order_comments\" AS \"order_comments\" 
                                    FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table 
                                GROUP BY \"warehouse_location\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Cost by Category
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"product_category"'],
                "rows": ['"sum(total_cost)"'],
                "custom_query": """SELECT \"product_category\" AS \"product_category\", 
                                        SUM(\"total_cost\") AS \"sum(total_cost)\" 
                                    FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", 
                                                \"supply_chain\".\"order_date\" AS \"order_date\", 
                                                \"supply_chain\".\"supplier_id\" AS \"supplier_id\", 
                                                \"supply_chain\".\"supplier_name\" AS \"supplier_name\", 
                                                \"supply_chain\".\"product_id\" AS \"product_id\", 
                                                \"supply_chain\".\"product_name\" AS \"product_name\", 
                                                \"supply_chain\".\"product_category\" AS \"product_category\", 
                                                \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                                \"supply_chain\".\"quantity_received\" AS \"quantity_received\", 
                                                \"supply_chain\".\"order_status\" AS \"order_status\", 
                                                \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", 
                                                \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", 
                                                \"supply_chain\".\"total_cost\" AS \"total_cost\", 
                                                \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", 
                                                \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", 
                                                \"supply_chain\".\"inventory_level\" AS \"inventory_level\", 
                                                \"supply_chain\".\"backorder_status\" AS \"backorder_status\", 
                                                \"supply_chain\".\"delivery_date\" AS \"delivery_date\", 
                                                \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", 
                                                \"supply_chain\".\"order_comments\" AS \"order_comments\" 
                                        FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table 
                                    GROUP BY \"product_category\"
                                    """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            # Supplier Wise Rating
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"supplier_name"'],
                "rows": ['"avg(supplier_rating)"'],
                "custom_query": """
                                SELECT \"supplier_name\" AS \"supplier_name\", 
                                    AVG(\"supplier_rating\") AS \"avg(supplier_rating)\" 
                                FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", 
                                            \"supply_chain\".\"order_date\" AS \"order_date\", 
                                            \"supply_chain\".\"supplier_id\" AS \"supplier_id\", 
                                            \"supply_chain\".\"supplier_name\" AS \"supplier_name\", 
                                            \"supply_chain\".\"product_id\" AS \"product_id\", 
                                            \"supply_chain\".\"product_name\" AS \"product_name\", 
                                            \"supply_chain\".\"product_category\" AS \"product_category\", 
                                            \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"supply_chain\".\"quantity_received\" AS \"quantity_received\", 
                                            \"supply_chain\".\"order_status\" AS \"order_status\", 
                                            \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", 
                                            \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", 
                                            \"supply_chain\".\"total_cost\" AS \"total_cost\", 
                                            \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", 
                                            \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", 
                                            \"supply_chain\".\"inventory_level\" AS \"inventory_level\", 
                                            \"supply_chain\".\"backorder_status\" AS \"backorder_status\", 
                                            \"supply_chain\".\"delivery_date\" AS \"delivery_date\", 
                                            \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", 
                                            \"supply_chain\".\"order_comments\" AS \"order_comments\" 
                                    FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table 
                                GROUP BY \"supplier_name\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },     
            # Supply Chain Overview           
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": ['"order_id"', '"product_id"', '"product_name"', '"product_category"', '"total_cost"', '"shipping_cost"'],
                "rows": [],
                "custom_query": """
                                SELECT \"order_id\" AS \"order_id\", 
                                    \"product_id\" AS \"product_id\", 
                                    \"product_name\" AS \"product_name\", 
                                    \"product_category\" AS \"product_category\", 
                                    \"total_cost\" AS \"total_cost\", 
                                    \"shipping_cost\" AS \"shipping_cost\" 
                                FROM (SELECT \"supply_chain\".\"order_id\" AS \"order_id\", 
                                            \"supply_chain\".\"order_date\" AS \"order_date\", 
                                            \"supply_chain\".\"supplier_id\" AS \"supplier_id\", 
                                            \"supply_chain\".\"supplier_name\" AS \"supplier_name\", 
                                            \"supply_chain\".\"product_id\" AS \"product_id\", 
                                            \"supply_chain\".\"product_name\" AS \"product_name\", 
                                            \"supply_chain\".\"product_category\" AS \"product_category\", 
                                            \"supply_chain\".\"quantity_ordered\" AS \"quantity_ordered\", 
                                            \"supply_chain\".\"quantity_received\" AS \"quantity_received\", 
                                            \"supply_chain\".\"order_status\" AS \"order_status\", 
                                            \"supply_chain\".\"lead_time_days\" AS \"lead_time_days\", 
                                            \"supply_chain\".\"cost_per_unit\" AS \"cost_per_unit\", 
                                            \"supply_chain\".\"total_cost\" AS \"total_cost\", 
                                            \"supply_chain\".\"shipping_cost\" AS \"shipping_cost\", 
                                            \"supply_chain\".\"warehouse_location\" AS \"warehouse_location\", 
                                            \"supply_chain\".\"inventory_level\" AS \"inventory_level\", 
                                            \"supply_chain\".\"backorder_status\" AS \"backorder_status\", 
                                            \"supply_chain\".\"delivery_date\" AS \"delivery_date\", 
                                            \"supply_chain\".\"supplier_rating\" AS \"supplier_rating\", 
                                            \"supply_chain\".\"order_comments\" AS \"order_comments\" 
                                    FROM \"In Ex\".\"supply_chain\" AS \"supply_chain\") temp_table 
                                GROUP BY \"order_id\", 
                                        \"product_id\", 
                                        \"product_name\", 
                                        \"product_category\", 
                                        \"total_cost\", 
                                        \"shipping_cost\"
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

        sheet_filter_querysets = models.SheetFilter_querysets.objects.filter(
            user_id=user_id, queryset_id=querysetid.queryset_id).values_list('Sheetqueryset_id', flat=True).order_by('Sheetqueryset_id')
        sheetData = [
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Orders",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.1-Total Orders.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Orders</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Suppliers",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.2-Total Suppliers.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Suppliers</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Products",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.3-Total Products.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Products</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Quantity Ordered",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.4-Quantity Ordered.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Quantity Ordered</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Quantity Received",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.5-Quantity Received.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Quantity Received</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 6,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Cost by Order date drill down",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.6-Total Cost by Order date drill down.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Cost by Order date drill down</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 2,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Region wise quantity ordered and received",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.7-Region wise quantity ordered and received.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Region wise quantity ordered and received</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 10,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Cost by Category",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.8-Cost by Category.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Cost by Category</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 6,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Supplier wise rating",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.9-Supplier wise rating.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Supplier wise rating</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 1,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Supply chain overview",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '5.10-Supply chain overview.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Supply chain overview</strong></span></p>""",
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
            input_file_name = 'Dashboard-SupplyChain.txt'
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', input_file_name)

            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)

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

            image_file_name = 'supplyChainDashboardImage.jpeg'
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
            print(f"Error: {e}")
            return {"error": str(e)}
        
        dashboardSampleData = {
            "user_id": user_id,
            "hierarchy_id": [hierarchy_id],
            "queryset_id": [querysetid.queryset_id],
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "1800",
            "width": "800",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "Supply Chain Dashboard",
            "datapath": output_file_key,
            "datasrc": file_url,
            "imagepath": output_image_key,
            "imagesrc": image_url,
            "dashboard_tag_name": """<p style="text-align:center;"><span style="color:hsl(0, 0%, 0%);font-size:16px;"><strong>Supply Chain Dashboard</strong></span></p>""",
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
        
        dashbaordFiltersSampleData = [
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list,
                "filter_name": "Category",
                "table_name": "supply_chain",
                "column_name": "product_category",
                "column_datatype": "string",
                "hierarchy_id" : hierarchy_id,
                "queryset_id": [querysetid.queryset_id],
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list,
                "filter_name": "Supplier Name",
                "table_name": "supply_chain",
                "column_name": "supplier_name",
                "column_datatype": "string",
                "hierarchy_id" : hierarchy_id,
                "queryset_id": [querysetid.queryset_id],
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "dashboard_id": dashboard_data_instance.id,
                "sheet_id_list": sheet_ids_list,
                "filter_name": "Region",
                "table_name": "supply_chain",
                "column_name": "warehouse_location",
                "column_datatype": "string",
                "hierarchy_id" : hierarchy_id,
                "queryset_id": [querysetid.queryset_id],
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
                    hierarchy_id=filter_data["hierarchy_id"],
                    selected_query = querysetid.queryset_id,
                    queryset_id=filter_data["queryset_id"] or None,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )
            
            self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashboard Filter Data'))
        except Exception as e:
            pass