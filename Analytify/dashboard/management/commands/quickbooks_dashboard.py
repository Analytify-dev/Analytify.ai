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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-quickbooks Data.txt'), 'r') as txt_file:
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
            "table_names": [['In Ex', 'quickbooks', 'quickbooks']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": """SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" 
                                FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\"
                            """,
            "query_name": "Quickbooks",
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
                "rows": ['"count(pr_Id)"'],
                "custom_query": """
                                SELECT COUNT(\"pr_Id\") AS \"count(pr_Id)\" 
                                FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table
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
                "filter_id_list": [87],
                "columns": [],
                "rows": ['"count(Active)"'],
                "custom_query": """
                                SELECT COUNT(\"Active\") AS \"count(Active)\" 
                                FROM (SELECT \"quickbooks\".\"id\" AS \"id\", 
                                            \"quickbooks\".\"Taxable\" AS \"Taxable\", 
                                            \"quickbooks\".\"Job\" AS \"Job\", 
                                            \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", 
                                            \"quickbooks\".\"Balance\" AS \"Balance\", 
                                            \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", 
                                            \"quickbooks\".\"value\" AS \"value\", 
                                            \"quickbooks\".\"name\" AS \"name\", 
                                            \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", 
                                            \"quickbooks\".\"IsProject\" AS \"IsProject\", 
                                            \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", 
                                            \"quickbooks\".\"domain\" AS \"domain\", 
                                            \"quickbooks\".\"sparse\" AS \"sparse\", 
                                            \"quickbooks\".\"SyncToken\" AS \"SyncToken\", 
                                            \"quickbooks\".\"CreateTime\" AS \"CreateTime\", 
                                            \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", 
                                            \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", 
                                            \"quickbooks\".\"DisplayName\" AS \"DisplayName\", 
                                            \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", 
                                            \"quickbooks\".\"Active\" AS \"Active\", 
                                            \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", 
                                            \"quickbooks\".\"Address\" AS \"Address\", 
                                            \"quickbooks\".\"Line1\" AS \"Line1\", 
                                            \"quickbooks\".\"City\" AS \"City\", 
                                            \"quickbooks\".\"Country\" AS \"Country\", 
                                            \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", 
                                            \"quickbooks\".\"PostalCode\" AS \"PostalCode\", 
                                            \"quickbooks\".\"Notes\" AS \"Notes\", 
                                            \"quickbooks\".\"Title\" AS \"Title\", 
                                            \"quickbooks\".\"GivenName\" AS \"GivenName\", 
                                            \"quickbooks\".\"MiddleName\" AS \"MiddleName\", 
                                            \"quickbooks\".\"FamilyName\" AS \"FamilyName\", 
                                            \"quickbooks\".\"Suffix\" AS \"Suffix\", 
                                            \"quickbooks\".\"CompanyName\" AS \"CompanyName\", 
                                            \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", 
                                            \"quickbooks\".\"Lat\" AS \"Lat\", 
                                            \"quickbooks\".\"Long\" AS \"Long\", 
                                            \"quickbooks\".\"URI\" AS \"URI\", 
                                            \"quickbooks\".\"Level\" AS \"Level\", 
                                            \"quickbooks\".\"startPosition\" AS \"startPosition\", 
                                            \"quickbooks\".\"maxResults\" AS \"maxResults\", 
                                            \"quickbooks\".\"time\" AS \"time\", 
                                            \"quickbooks\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table 
                                WHERE \"Active\" IN ('1')
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
                "filter_id_list": [88],
                "columns": [],
                "rows": ['"count(Active)"'],
                "custom_query": """
                                SELECT COUNT(\"Active\") AS \"count(Active)\" 
                                FROM (SELECT \"quickbooks\".\"id\" AS \"id\", 
                                            \"quickbooks\".\"Taxable\" AS \"Taxable\", 
                                            \"quickbooks\".\"Job\" AS \"Job\", 
                                            \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", 
                                            \"quickbooks\".\"Balance\" AS \"Balance\", 
                                            \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", 
                                            \"quickbooks\".\"value\" AS \"value\", 
                                            \"quickbooks\".\"name\" AS \"name\", 
                                            \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", 
                                            \"quickbooks\".\"IsProject\" AS \"IsProject\", 
                                            \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", 
                                            \"quickbooks\".\"domain\" AS \"domain\", 
                                            \"quickbooks\".\"sparse\" AS \"sparse\", 
                                            \"quickbooks\".\"SyncToken\" AS \"SyncToken\", 
                                            \"quickbooks\".\"CreateTime\" AS \"CreateTime\", 
                                            \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", 
                                            \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", 
                                            \"quickbooks\".\"DisplayName\" AS \"DisplayName\", 
                                            \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", 
                                            \"quickbooks\".\"Active\" AS \"Active\", 
                                            \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", 
                                            \"quickbooks\".\"Address\" AS \"Address\", 
                                            \"quickbooks\".\"Line1\" AS \"Line1\", 
                                            \"quickbooks\".\"City\" AS \"City\", 
                                            \"quickbooks\".\"Country\" AS \"Country\", 
                                            \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", 
                                            \"quickbooks\".\"PostalCode\" AS \"PostalCode\", 
                                            \"quickbooks\".\"Notes\" AS \"Notes\", 
                                            \"quickbooks\".\"Title\" AS \"Title\", 
                                            \"quickbooks\".\"GivenName\" AS \"GivenName\", 
                                            \"quickbooks\".\"MiddleName\" AS \"MiddleName\", 
                                            \"quickbooks\".\"FamilyName\" AS \"FamilyName\", 
                                            \"quickbooks\".\"Suffix\" AS \"Suffix\", 
                                            \"quickbooks\".\"CompanyName\" AS \"CompanyName\", 
                                            \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", 
                                            \"quickbooks\".\"Lat\" AS \"Lat\", 
                                            \"quickbooks\".\"Long\" AS \"Long\", 
                                            \"quickbooks\".\"URI\" AS \"URI\", 
                                            \"quickbooks\".\"Level\" AS \"Level\", 
                                            \"quickbooks\".\"startPosition\" AS \"startPosition\", 
                                            \"quickbooks\".\"maxResults\" AS \"maxResults\", 
                                            \"quickbooks\".\"time\" AS \"time\", 
                                            \"quickbooks\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table 
                                WHERE \"Active\" IN ('0')
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
                "rows": ['"sum(Balance)"'],
                "custom_query": """ SELECT SUM(\"Balance\") AS \"sum(Balance)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table"
                                """,
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
                "rows": ['"sum(BalanceWithJobs)"'],
                "custom_query": """ SELECT SUM(\"BalanceWithJobs\") AS \"sum(BalanceWithJobs)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table
                                """,
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
                "columns": ['"year(CreateTime)"'],
                "rows": ['"sum(Balance)"'],
                "custom_query": """ SELECT DATE_FORMAT(CAST(\"CreateTime\" AS TIMESTAMP), '%Y') AS \"year(CreateTime)\", SUM(\"Balance\") AS \"sum(Balance)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table GROUP BY \"year(CreateTime)\", \"year(CreateTime)\"
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
                "columns": [' "PreferredDeliveryMethod"'],
                "rows": ['"count(pr_Id)"'],
                "custom_query": """SELECT \"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", COUNT(\"pr_Id\") AS \"count(pr_Id)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table GROUP BY \"PreferredDeliveryMethod\", \"PreferredDeliveryMethod\"ain\" AS \"supply_chain\") temp_table 
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
                "columns": [' "Title"'],
                "rows": ['"count(pr_Id)"'],
                "custom_query": """
                                SELECT \"Title\" AS \"Title\", COUNT(\"pr_Id\") AS \"count(pr_Id)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table GROUP BY \"Title\", \"Title\"
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
                "columns": [' "Country"'],
                "rows": ['"sum(Balance)"'],
                "custom_query": """
                                =SELECT \"Country\" AS \"Country\", SUM(\"Balance\") AS \"sum(Balance)\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table GROUP BY \"Country\", \"Country\"
                                """,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "datasource_querysetid": "",
                "queryset_id": querysetid.queryset_id,
                "user_id": user_id,
                "hierarchy_id":hierarchy_id,
                "filter_id_list": [],
                "columns": [' "pr_Id"', ' "CompanyName"', ' "domain"', ' "Country"', ' "Balance"', ' "BalanceWithJobs"'],
                "rows": [],
                "custom_query": """
                                SELECT \"pr_Id\" AS \"pr_Id\", \"CompanyName\" AS \"CompanyName\", \"domain\" AS \"domain\", \"Country\" AS \"Country\", \"Balance\" AS \"Balance\", \"BalanceWithJobs\" AS \"BalanceWithJobs\" FROM (SELECT \"quickbooks\".\"id\" AS \"id\", \"quickbooks\".\"Taxable\" AS \"Taxable\", \"quickbooks\".\"Job\" AS \"Job\", \"quickbooks\".\"BillWithParent\" AS \"BillWithParent\", \"quickbooks\".\"Balance\" AS \"Balance\", \"quickbooks\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"quickbooks\".\"value\" AS \"value\", \"quickbooks\".\"name\" AS \"name\", \"quickbooks\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"quickbooks\".\"IsProject\" AS \"IsProject\", \"quickbooks\".\"ClientEntityId\" AS \"ClientEntityId\", \"quickbooks\".\"domain\" AS \"domain\", \"quickbooks\".\"sparse\" AS \"sparse\", \"quickbooks\".\"SyncToken\" AS \"SyncToken\", \"quickbooks\".\"CreateTime\" AS \"CreateTime\", \"quickbooks\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"quickbooks\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"quickbooks\".\"DisplayName\" AS \"DisplayName\", \"quickbooks\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"quickbooks\".\"Active\" AS \"Active\", \"quickbooks\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"quickbooks\".\"Address\" AS \"Address\", \"quickbooks\".\"Line1\" AS \"Line1\", \"quickbooks\".\"City\" AS \"City\", \"quickbooks\".\"Country\" AS \"Country\", \"quickbooks\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"quickbooks\".\"PostalCode\" AS \"PostalCode\", \"quickbooks\".\"Notes\" AS \"Notes\", \"quickbooks\".\"Title\" AS \"Title\", \"quickbooks\".\"GivenName\" AS \"GivenName\", \"quickbooks\".\"MiddleName\" AS \"MiddleName\", \"quickbooks\".\"FamilyName\" AS \"FamilyName\", \"quickbooks\".\"Suffix\" AS \"Suffix\", \"quickbooks\".\"CompanyName\" AS \"CompanyName\", \"quickbooks\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"quickbooks\".\"Lat\" AS \"Lat\", \"quickbooks\".\"Long\" AS \"Long\", \"quickbooks\".\"URI\" AS \"URI\", \"quickbooks\".\"Level\" AS \"Level\", \"quickbooks\".\"startPosition\" AS \"startPosition\", \"quickbooks\".\"maxResults\" AS \"maxResults\", \"quickbooks\".\"time\" AS \"time\", \"quickbooks\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"quickbooks\" AS \"quickbooks\") temp_table GROUP BY \"pr_Id\", \"CompanyName\", \"domain\", \"Country\", \"Balance\", \"BalanceWithJobs\", \"pr_Id\", \"CompanyName\", \"domain\", \"Country\", \"Balance\", \"BalanceWithJobs\"
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
        print(sheet_filter_querysets)
        sheetData = [
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Customers",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.1-Total Customers.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Customers</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [87],
                "sheet_name": "Active Customers",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.2-Active Customers.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Active Customers</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [88],
                "sheet_name": "Inactive Customers",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.3-Inactive Customers.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Inactive Customers</strong></span></p>""",
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
                "sheet_name": "Total Balance",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.4-Total Balance.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Balance</strong></span></p>""",
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
                "sheet_name": "Total Balance with Jobs",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.5-Total Balance with Jobs.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Balance with Jobs</strong></span></p>""",
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
                "sheet_name": "Year Wise Balance",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.6-Year Wise Balance.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Year Wise Balance</strong></span></p>""",
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
                "sheet_name": "Customer segmentation by delivery method",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.7-Customer segmentation by delivery method.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Customer segmentation by delivery method</strong></span></p>""",
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
                "sheet_name": "Title wise Customer Count",
                "sheetfilter_querysets_id": sheet_filter_querysets[7],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.8-Title wise Customer Count.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Title wise Customer Count</strong></span></p>""",
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
                "sheet_name": "Country Wise Balance",
                "sheetfilter_querysets_id": sheet_filter_querysets[8],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.9-Country Wise Balance.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Country Wise Balance</strong></span></p>""",
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
                "sheet_name": "Quickbooks Customer Overview",
                "sheetfilter_querysets_id": sheet_filter_querysets[9],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '6.10-Quickbooks Customer Overview.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Quickbooks Customer Overview</strong></span></p>""",
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
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'Dashboard-quickbooks dashboard.txt')

            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)

            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = hierarchy_id
                item['qrySetId'] = querysetid.queryset_id

            file_url, output_file_key = create_s3_file(input_file_path, sheet_ids_list, hierarchy_id, querysetid, bucket_name)

            image_image_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'images', 'quickbooks.jpeg')

            current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")

            image_url, output_image_key = create_s3_image(image_image_path, current_datetime, bucket_name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return Response({"message": str(e)}, status=400)

        dashboardSampleData = {
            "user_id": user_id,
            "hierarchy_id":[hierarchy_id],
            "queryset_id": [querysetid.queryset_id],
            "sheet_ids": [sheet_ids_list],
            "selected_sheet_ids": [sheet_ids_list],
            "height": "1800",
            "width": "800",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "QuickBooks Analytics Dashboard",
            "datapath": output_file_key,
            "datasrc": file_url,
            "imagepath": output_image_key,
            "imagesrc": image_url,
            "dashboard_tag_name": """<p style="text-align:center;"><span style="color:hsl(0, 0%, 0%);font-size:16px;"><strong>QuickBooks Analytics Dashboard</strong></span></p>""",
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
        #         "filter_name": "Category",
        #         "table_name": "supply_chain",
        #         "column_name": "product_category",
        #         "column_datatype": "string",
        #         "queryset_id": querysetid.queryset_id,
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "dashboard_id": dashboard_data_instance.id,
        #         "sheet_id_list": sheet_ids_list,
        #         "filter_name": "Supplier Name",
        #         "table_name": "supply_chain",
        #         "column_name": "supplier_name",
        #         "column_datatype": "string",
        #         "queryset_id": querysetid.queryset_id,
        #         "created_at": datetime.datetime.now(),
        #         "updated_at": datetime.datetime.now()
        #     },
        #     {
        #         "user_id": user_id,
        #         "dashboard_id": dashboard_data_instance.id,
        #         "sheet_id_list": sheet_ids_list,
        #         "filter_name": "Region",
        #         "table_name": "supply_chain",
        #         "column_name": "warehouse_location",
        #         "column_datatype": "string",
        #         "queryset_id": querysetid.queryset_id,
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
        #             queryset_id=filter_data["queryset_id"] or None,
        #             created_at=datetime.datetime.now(),
        #             updated_at=datetime.datetime.now(),
        #         )
            
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashboard Filter Data'))
        # except Exception as e:
        #     pass