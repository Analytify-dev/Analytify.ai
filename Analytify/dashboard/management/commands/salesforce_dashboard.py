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
        with open(os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'datasource', 'Queryset-salesforce Data.txt'), 'r') as txt_file:
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
            "table_names": [['In Ex', 'salesforce', 'salesforce']],
            "join_type": [],
            "joining_conditions": [],
            "is_custom_sql": False,
            "custom_query": """SELECT \"salesforce\".\"id\" AS \"id\", \"salesforce\".\"totalSize\" AS \"totalSize\", \"salesforce\".\"done\" AS \"done\", \"salesforce\".\"type\" AS \"type\", \"salesforce\".\"url\" AS \"url\", \"salesforce\".\"Username\" AS \"Username\", \"salesforce\".\"LastName\" AS \"LastName\", \"salesforce\".\"FirstName\" AS \"FirstName\", \"salesforce\".\"Name\" AS \"Name\", \"salesforce\".\"CompanyName\" AS \"CompanyName\", \"salesforce\".\"Division\" AS \"Division\", \"salesforce\".\"Department\" AS \"Department\", \"salesforce\".\"Title\" AS \"Title\", \"salesforce\".\"Street\" AS \"Street\", \"salesforce\".\"City\" AS \"City\", \"salesforce\".\"State\" AS \"State\", \"salesforce\".\"PostalCode\" AS \"PostalCode\", \"salesforce\".\"Country\" AS \"Country\", \"salesforce\".\"Latitude\" AS \"Latitude\", \"salesforce\".\"Longitude\" AS \"Longitude\", \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", \"salesforce\".\"Email\" AS \"Email\", \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", \"salesforce\".\"SenderName\" AS \"SenderName\", \"salesforce\".\"Signature\" AS \"Signature\", \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", \"salesforce\".\"Phone\" AS \"Phone\", \"salesforce\".\"Fax\" AS \"Fax\", \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", \"salesforce\".\"Alias\" AS \"Alias\", \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", \"salesforce\".\"BadgeText\" AS \"BadgeText\", \"salesforce\".\"IsActive\" AS \"IsActive\", \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", \"salesforce\".\"ProfileId\" AS \"ProfileId\", \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", \"salesforce\".\"ManagerId\" AS \"ManagerId\", \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", \"salesforce\".\"CreatedById\" AS \"CreatedById\", \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", \"salesforce\".\"pr_Id\" AS \"pr_Id\" FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                            """,
            "query_name": "salesforce",
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
                                FROM (
                                    SELECT 
                                        \"salesforce\".\"id\" AS \"id\", 
                                        \"salesforce\".\"totalSize\" AS \"totalSize\", 
                                        \"salesforce\".\"done\" AS \"done\", 
                                        \"salesforce\".\"type\" AS \"type\", 
                                        \"salesforce\".\"url\" AS \"url\", 
                                        \"salesforce\".\"Username\" AS \"Username\", 
                                        \"salesforce\".\"LastName\" AS \"LastName\", 
                                        \"salesforce\".\"FirstName\" AS \"FirstName\", 
                                        \"salesforce\".\"Name\" AS \"Name\", 
                                        \"salesforce\".\"CompanyName\" AS \"CompanyName\", 
                                        \"salesforce\".\"Division\" AS \"Division\", 
                                        \"salesforce\".\"Department\" AS \"Department\", 
                                        \"salesforce\".\"Title\" AS \"Title\", 
                                        \"salesforce\".\"Street\" AS \"Street\", 
                                        \"salesforce\".\"City\" AS \"City\", 
                                        \"salesforce\".\"State\" AS \"State\", 
                                        \"salesforce\".\"PostalCode\" AS \"PostalCode\", 
                                        \"salesforce\".\"Country\" AS \"Country\", 
                                        \"salesforce\".\"Latitude\" AS \"Latitude\", 
                                        \"salesforce\".\"Longitude\" AS \"Longitude\", 
                                        \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", 
                                        \"salesforce\".\"Email\" AS \"Email\", 
                                        \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", 
                                        \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", 
                                        \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", 
                                        \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", 
                                        \"salesforce\".\"SenderName\" AS \"SenderName\", 
                                        \"salesforce\".\"Signature\" AS \"Signature\", 
                                        \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", 
                                        \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", 
                                        \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", 
                                        \"salesforce\".\"Phone\" AS \"Phone\", 
                                        \"salesforce\".\"Fax\" AS \"Fax\", 
                                        \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", 
                                        \"salesforce\".\"Alias\" AS \"Alias\", 
                                        \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", 
                                        \"salesforce\".\"BadgeText\" AS \"BadgeText\", 
                                        \"salesforce\".\"IsActive\" AS \"IsActive\", 
                                        \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", 
                                        \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", 
                                        \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", 
                                        \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", 
                                        \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", 
                                        \"salesforce\".\"ProfileId\" AS \"ProfileId\", 
                                        \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", 
                                        \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", 
                                        \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", 
                                        \"salesforce\".\"ManagerId\" AS \"ManagerId\", 
                                        \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", 
                                        \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", 
                                        \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", 
                                        \"salesforce\".\"CreatedById\" AS \"CreatedById\", 
                                        \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", 
                                        \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", 
                                        \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", 
                                        \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", 
                                        \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", 
                                        \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", 
                                        \"salesforce\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
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
                "filter_id_list": [91],
                "columns": [],
                "rows": ['"count(pr_Id)"'],
                "custom_query": """
                                SELECT COUNT(\"pr_Id\") AS \"count(pr_Id)\"
                                FROM (
                                    SELECT 
                                        \"salesforce\".\"id\" AS \"id\", 
                                        \"salesforce\".\"totalSize\" AS \"totalSize\", 
                                        \"salesforce\".\"done\" AS \"done\", 
                                        \"salesforce\".\"type\" AS \"type\", 
                                        \"salesforce\".\"url\" AS \"url\", 
                                        \"salesforce\".\"Username\" AS \"Username\", 
                                        \"salesforce\".\"LastName\" AS \"LastName\", 
                                        \"salesforce\".\"FirstName\" AS \"FirstName\", 
                                        \"salesforce\".\"Name\" AS \"Name\", 
                                        \"salesforce\".\"CompanyName\" AS \"CompanyName\", 
                                        \"salesforce\".\"Division\" AS \"Division\", 
                                        \"salesforce\".\"Department\" AS \"Department\", 
                                        \"salesforce\".\"Title\" AS \"Title\", 
                                        \"salesforce\".\"Street\" AS \"Street\", 
                                        \"salesforce\".\"City\" AS \"City\", 
                                        \"salesforce\".\"State\" AS \"State\", 
                                        \"salesforce\".\"PostalCode\" AS \"PostalCode\", 
                                        \"salesforce\".\"Country\" AS \"Country\", 
                                        \"salesforce\".\"Latitude\" AS \"Latitude\", 
                                        \"salesforce\".\"Longitude\" AS \"Longitude\", 
                                        \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", 
                                        \"salesforce\".\"Email\" AS \"Email\", 
                                        \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", 
                                        \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", 
                                        \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", 
                                        \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", 
                                        \"salesforce\".\"SenderName\" AS \"SenderName\", 
                                        \"salesforce\".\"Signature\" AS \"Signature\", 
                                        \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", 
                                        \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", 
                                        \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", 
                                        \"salesforce\".\"Phone\" AS \"Phone\", 
                                        \"salesforce\".\"Fax\" AS \"Fax\", 
                                        \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", 
                                        \"salesforce\".\"Alias\" AS \"Alias\", 
                                        \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", 
                                        \"salesforce\".\"BadgeText\" AS \"BadgeText\", 
                                        \"salesforce\".\"IsActive\" AS \"IsActive\", 
                                        \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", 
                                        \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", 
                                        \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", 
                                        \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", 
                                        \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", 
                                        \"salesforce\".\"ProfileId\" AS \"ProfileId\", 
                                        \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", 
                                        \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", 
                                        \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", 
                                        \"salesforce\".\"ManagerId\" AS \"ManagerId\", 
                                        \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", 
                                        \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", 
                                        \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", 
                                        \"salesforce\".\"CreatedById\" AS \"CreatedById\", 
                                        \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", 
                                        \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", 
                                        \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", 
                                        \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", 
                                        \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", 
                                        \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", 
                                        \"salesforce\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
                                WHERE \"IsActive\" IN ('1')
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
                "filter_id_list": [92],
                "columns": [],
                "rows": ['"count(pr_Id)"'],
                "custom_query": """
                                SELECT COUNT(\"pr_Id\") AS \"count(pr_Id)\"
                                FROM (
                                    SELECT 
                                        \"salesforce\".\"id\" AS \"id\", 
                                        \"salesforce\".\"totalSize\" AS \"totalSize\", 
                                        \"salesforce\".\"done\" AS \"done\", 
                                        \"salesforce\".\"type\" AS \"type\", 
                                        \"salesforce\".\"url\" AS \"url\", 
                                        \"salesforce\".\"Username\" AS \"Username\", 
                                        \"salesforce\".\"LastName\" AS \"LastName\", 
                                        \"salesforce\".\"FirstName\" AS \"FirstName\", 
                                        \"salesforce\".\"Name\" AS \"Name\", 
                                        \"salesforce\".\"CompanyName\" AS \"CompanyName\", 
                                        \"salesforce\".\"Division\" AS \"Division\", 
                                        \"salesforce\".\"Department\" AS \"Department\", 
                                        \"salesforce\".\"Title\" AS \"Title\", 
                                        \"salesforce\".\"Street\" AS \"Street\", 
                                        \"salesforce\".\"City\" AS \"City\", 
                                        \"salesforce\".\"State\" AS \"State\", 
                                        \"salesforce\".\"PostalCode\" AS \"PostalCode\", 
                                        \"salesforce\".\"Country\" AS \"Country\", 
                                        \"salesforce\".\"Latitude\" AS \"Latitude\", 
                                        \"salesforce\".\"Longitude\" AS \"Longitude\", 
                                        \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", 
                                        \"salesforce\".\"Email\" AS \"Email\", 
                                        \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", 
                                        \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", 
                                        \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", 
                                        \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", 
                                        \"salesforce\".\"SenderName\" AS \"SenderName\", 
                                        \"salesforce\".\"Signature\" AS \"Signature\", 
                                        \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", 
                                        \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", 
                                        \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", 
                                        \"salesforce\".\"Phone\" AS \"Phone\", 
                                        \"salesforce\".\"Fax\" AS \"Fax\", 
                                        \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", 
                                        \"salesforce\".\"Alias\" AS \"Alias\", 
                                        \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", 
                                        \"salesforce\".\"BadgeText\" AS \"BadgeText\", 
                                        \"salesforce\".\"IsActive\" AS \"IsActive\", 
                                        \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", 
                                        \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", 
                                        \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", 
                                        \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", 
                                        \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", 
                                        \"salesforce\".\"ProfileId\" AS \"ProfileId\", 
                                        \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", 
                                        \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", 
                                        \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", 
                                        \"salesforce\".\"ManagerId\" AS \"ManagerId\", 
                                        \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", 
                                        \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", 
                                        \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", 
                                        \"salesforce\".\"CreatedById\" AS \"CreatedById\", 
                                        \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", 
                                        \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", 
                                        \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", 
                                        \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", 
                                        \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", 
                                        \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", 
                                        \"salesforce\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
                                WHERE \"IsActive\" IN ('0')
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
                "rows": ['"sum(NumberOfFailedLogins)"'],
                "custom_query": """ 
                                SELECT SUM(\"NumberOfFailedLogins\") AS \"sum(NumberOfFailedLogins)\"
                                FROM (
                                    SELECT 
                                        \"salesforce\".\"id\" AS \"id\", 
                                        \"salesforce\".\"totalSize\" AS \"totalSize\", 
                                        \"salesforce\".\"done\" AS \"done\", 
                                        \"salesforce\".\"type\" AS \"type\", 
                                        \"salesforce\".\"url\" AS \"url\", 
                                        \"salesforce\".\"Username\" AS \"Username\", 
                                        \"salesforce\".\"LastName\" AS \"LastName\", 
                                        \"salesforce\".\"FirstName\" AS \"FirstName\", 
                                        \"salesforce\".\"Name\" AS \"Name\", 
                                        \"salesforce\".\"CompanyName\" AS \"CompanyName\", 
                                        \"salesforce\".\"Division\" AS \"Division\", 
                                        \"salesforce\".\"Department\" AS \"Department\", 
                                        \"salesforce\".\"Title\" AS \"Title\", 
                                        \"salesforce\".\"Street\" AS \"Street\", 
                                        \"salesforce\".\"City\" AS \"City\", 
                                        \"salesforce\".\"State\" AS \"State\", 
                                        \"salesforce\".\"PostalCode\" AS \"PostalCode\", 
                                        \"salesforce\".\"Country\" AS \"Country\", 
                                        \"salesforce\".\"Latitude\" AS \"Latitude\", 
                                        \"salesforce\".\"Longitude\" AS \"Longitude\", 
                                        \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", 
                                        \"salesforce\".\"Email\" AS \"Email\", 
                                        \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", 
                                        \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", 
                                        \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", 
                                        \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", 
                                        \"salesforce\".\"SenderName\" AS \"SenderName\", 
                                        \"salesforce\".\"Signature\" AS \"Signature\", 
                                        \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", 
                                        \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", 
                                        \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", 
                                        \"salesforce\".\"Phone\" AS \"Phone\", 
                                        \"salesforce\".\"Fax\" AS \"Fax\", 
                                        \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", 
                                        \"salesforce\".\"Alias\" AS \"Alias\", 
                                        \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", 
                                        \"salesforce\".\"BadgeText\" AS \"BadgeText\", 
                                        \"salesforce\".\"IsActive\" AS \"IsActive\", 
                                        \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", 
                                        \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", 
                                        \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", 
                                        \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", 
                                        \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", 
                                        \"salesforce\".\"ProfileId\" AS \"ProfileId\", 
                                        \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", 
                                        \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", 
                                        \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", 
                                        \"salesforce\".\"ManagerId\" AS \"ManagerId\", 
                                        \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", 
                                        \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", 
                                        \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", 
                                        \"salesforce\".\"CreatedById\" AS \"CreatedById\", 
                                        \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", 
                                        \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", 
                                        \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", 
                                        \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", 
                                        \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", 
                                        \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", 
                                        \"salesforce\".\"pr_Id\" AS \"pr_Id\" 
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
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
                "columns": ['"year(CreatedDate)"'],
                "rows": ['"count(id)"'],
                "custom_query": """ 
                                SELECT DATE_FORMAT(CAST(\"CreatedDate\" AS TIMESTAMP), '%Y') AS \"year(CreatedDate)\", COUNT(\"id\") AS \"count(id)\"
                                FROM (
                                    SELECT \"salesforce\".\"id\" AS \"id\", \"salesforce\".\"totalSize\" AS \"totalSize\", \"salesforce\".\"done\" AS \"done\", \"salesforce\".\"type\" AS \"type\", \"salesforce\".\"url\" AS \"url\", \"salesforce\".\"Username\" AS \"Username\", \"salesforce\".\"LastName\" AS \"LastName\", \"salesforce\".\"FirstName\" AS \"FirstName\", \"salesforce\".\"Name\" AS \"Name\", \"salesforce\".\"CompanyName\" AS \"CompanyName\", \"salesforce\".\"Division\" AS \"Division\", \"salesforce\".\"Department\" AS \"Department\", \"salesforce\".\"Title\" AS \"Title\", \"salesforce\".\"Street\" AS \"Street\", \"salesforce\".\"City\" AS \"City\", \"salesforce\".\"State\" AS \"State\", \"salesforce\".\"PostalCode\" AS \"PostalCode\", \"salesforce\".\"Country\" AS \"Country\", \"salesforce\".\"Latitude\" AS \"Latitude\", \"salesforce\".\"Longitude\" AS \"Longitude\", \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", \"salesforce\".\"Email\" AS \"Email\", \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", \"salesforce\".\"SenderName\" AS \"SenderName\", \"salesforce\".\"Signature\" AS \"Signature\", \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", \"salesforce\".\"Phone\" AS \"Phone\", \"salesforce\".\"Fax\" AS \"Fax\", \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", \"salesforce\".\"Alias\" AS \"Alias\", \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", \"salesforce\".\"BadgeText\" AS \"BadgeText\", \"salesforce\".\"IsActive\" AS \"IsActive\", \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", \"salesforce\".\"ProfileId\" AS \"ProfileId\", \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", \"salesforce\".\"ManagerId\" AS \"ManagerId\", \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", \"salesforce\".\"CreatedById\" AS \"CreatedById\", \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", \"salesforce\".\"pr_Id\" AS \"pr_Id\"
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
                                GROUP BY \"year(CreatedDate)\", \"year(CreatedDate)\"
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
                "columns": [' "Country"'],
                "rows": ['"count(pr_Id)"'],
                "custom_query": """ SELECT \"Country\" AS \"Country\", COUNT(\"pr_Id\") AS \"count(pr_Id)\"
                                    FROM (
                                        SELECT \"salesforce\".\"id\" AS \"id\", \"salesforce\".\"totalSize\" AS \"totalSize\", \"salesforce\".\"done\" AS \"done\", \"salesforce\".\"type\" AS \"type\", \"salesforce\".\"url\" AS \"url\", \"salesforce\".\"Username\" AS \"Username\", \"salesforce\".\"LastName\" AS \"LastName\", \"salesforce\".\"FirstName\" AS \"FirstName\", \"salesforce\".\"Name\" AS \"Name\", \"salesforce\".\"CompanyName\" AS \"CompanyName\", \"salesforce\".\"Division\" AS \"Division\", \"salesforce\".\"Department\" AS \"Department\", \"salesforce\".\"Title\" AS \"Title\", \"salesforce\".\"Street\" AS \"Street\", \"salesforce\".\"City\" AS \"City\", \"salesforce\".\"State\" AS \"State\", \"salesforce\".\"PostalCode\" AS \"PostalCode\", \"salesforce\".\"Country\" AS \"Country\", \"salesforce\".\"Latitude\" AS \"Latitude\", \"salesforce\".\"Longitude\" AS \"Longitude\", \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", \"salesforce\".\"Email\" AS \"Email\", \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", \"salesforce\".\"SenderName\" AS \"SenderName\", \"salesforce\".\"Signature\" AS \"Signature\", \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", \"salesforce\".\"Phone\" AS \"Phone\", \"salesforce\".\"Fax\" AS \"Fax\", \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", \"salesforce\".\"Alias\" AS \"Alias\", \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", \"salesforce\".\"BadgeText\" AS \"BadgeText\", \"salesforce\".\"IsActive\" AS \"IsActive\", \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", \"salesforce\".\"ProfileId\" AS \"ProfileId\", \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", \"salesforce\".\"ManagerId\" AS \"ManagerId\", \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", \"salesforce\".\"CreatedById\" AS \"CreatedById\", \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", \"salesforce\".\"pr_Id\" AS \"pr_Id\"
                                        FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                    ) temp_table
                                    GROUP BY \"Country\", \"Country\"
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
                "columns": [' "EmployeeNumber"', ' "Username"', ' "Email"', ' "CompanyName"', ' "Department"', ' "Title"', ' "Country"'],
                "rows": [],
                "custom_query": """
                                SELECT \"EmployeeNumber\" AS \"EmployeeNumber\", \"Username\" AS \"Username\", \"Email\" AS \"Email\", \"CompanyName\" AS \"CompanyName\", \"Department\" AS \"Department\", \"Title\" AS \"Title\", \"Country\" AS \"Country\"
                                FROM (
                                    SELECT \"salesforce\".\"id\" AS \"id\", \"salesforce\".\"totalSize\" AS \"totalSize\", \"salesforce\".\"done\" AS \"done\", \"salesforce\".\"type\" AS \"type\", \"salesforce\".\"url\" AS \"url\", \"salesforce\".\"Username\" AS \"Username\", \"salesforce\".\"LastName\" AS \"LastName\", \"salesforce\".\"FirstName\" AS \"FirstName\", \"salesforce\".\"Name\" AS \"Name\", \"salesforce\".\"CompanyName\" AS \"CompanyName\", \"salesforce\".\"Division\" AS \"Division\", \"salesforce\".\"Department\" AS \"Department\", \"salesforce\".\"Title\" AS \"Title\", \"salesforce\".\"Street\" AS \"Street\", \"salesforce\".\"City\" AS \"City\", \"salesforce\".\"State\" AS \"State\", \"salesforce\".\"PostalCode\" AS \"PostalCode\", \"salesforce\".\"Country\" AS \"Country\", \"salesforce\".\"Latitude\" AS \"Latitude\", \"salesforce\".\"Longitude\" AS \"Longitude\", \"salesforce\".\"GeocodeAccuracy\" AS \"GeocodeAccuracy\", \"salesforce\".\"Email\" AS \"Email\", \"salesforce\".\"EmailPreferencesAutoBcc\" AS \"EmailPreferencesAutoBcc\", \"salesforce\".\"EmailPreferencesAutoBccStayInTouch\" AS \"EmailPreferencesAutoBccStayInTouch\", \"salesforce\".\"EmailPreferencesStayInTouchReminder\" AS \"EmailPreferencesStayInTouchReminder\", \"salesforce\".\"SenderEmail\" AS \"SenderEmail\", \"salesforce\".\"SenderName\" AS \"SenderName\", \"salesforce\".\"Signature\" AS \"Signature\", \"salesforce\".\"StayInTouchSubject\" AS \"StayInTouchSubject\", \"salesforce\".\"StayInTouchSignature\" AS \"StayInTouchSignature\", \"salesforce\".\"StayInTouchNote\" AS \"StayInTouchNote\", \"salesforce\".\"Phone\" AS \"Phone\", \"salesforce\".\"Fax\" AS \"Fax\", \"salesforce\".\"MobilePhone\" AS \"MobilePhone\", \"salesforce\".\"Alias\" AS \"Alias\", \"salesforce\".\"CommunityNickname\" AS \"CommunityNickname\", \"salesforce\".\"BadgeText\" AS \"BadgeText\", \"salesforce\".\"IsActive\" AS \"IsActive\", \"salesforce\".\"TimeZoneSidKey\" AS \"TimeZoneSidKey\", \"salesforce\".\"LocaleSidKey\" AS \"LocaleSidKey\", \"salesforce\".\"ReceivesInfoEmails\" AS \"ReceivesInfoEmails\", \"salesforce\".\"ReceivesAdminInfoEmails\" AS \"ReceivesAdminInfoEmails\", \"salesforce\".\"EmailEncodingKey\" AS \"EmailEncodingKey\", \"salesforce\".\"ProfileId\" AS \"ProfileId\", \"salesforce\".\"LanguageLocaleKey\" AS \"LanguageLocaleKey\", \"salesforce\".\"EmployeeNumber\" AS \"EmployeeNumber\", \"salesforce\".\"DelegatedApproverId\" AS \"DelegatedApproverId\", \"salesforce\".\"ManagerId\" AS \"ManagerId\", \"salesforce\".\"LastLoginDate\" AS \"LastLoginDate\", \"salesforce\".\"LastPasswordChangeDate\" AS \"LastPasswordChangeDate\", \"salesforce\".\"CreatedDate\" AS \"CreatedDate\", \"salesforce\".\"CreatedById\" AS \"CreatedById\", \"salesforce\".\"LastModifiedDate\" AS \"LastModifiedDate\", \"salesforce\".\"LastModifiedById\" AS \"LastModifiedById\", \"salesforce\".\"SystemModstamp\" AS \"SystemModstamp\", \"salesforce\".\"NumberOfFailedLogins\" AS \"NumberOfFailedLogins\", \"salesforce\".\"OfflineTrialExpirationDate\" AS \"OfflineTrialExpirationDate\", \"salesforce\".\"OfflinePdaTrialExpirationDate\" AS \"OfflinePdaTrialExpirationDate\", \"salesforce\".\"pr_Id\" AS \"pr_Id\"
                                    FROM \"In Ex\".\"salesforce\" AS \"salesforce\"
                                ) temp_table
                                GROUP BY \"EmployeeNumber\", \"Username\", \"Email\", \"CompanyName\", \"Department\", \"Title\", \"Country\", \"EmployeeNumber\", \"Username\", \"Email\", \"CompanyName\", \"Department\", \"Title\", \"Country\"
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
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [],
                "sheet_name": "Total Users",
                "sheetfilter_querysets_id": sheet_filter_querysets[0],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.1-Total Users.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Total Users</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [91],
                "sheet_name": "Active Users",
                "sheetfilter_querysets_id": sheet_filter_querysets[1],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.2-Active Users.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Active Users</strong></span></p>""",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            },
            {
                "user_id": user_id,
                "chart_id": 25,
                "hierarchy_id": hierarchy_id,
                # "file_id": "",
                "queryset_id": querysetid.queryset_id,
                "filter_ids": [92],
                "sheet_name": "Inactive Users",
                "sheetfilter_querysets_id": sheet_filter_querysets[2],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.3-Inactive Users.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Inactive Users</strong></span></p>""",
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
                "sheet_name": "Failed Login Attempts",
                "sheetfilter_querysets_id": sheet_filter_querysets[3],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.4-Failed Login Attempts.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Failed Login Attempts</strong></span></p>""",
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
                "sheet_name": "Count of users by year",
                "sheetfilter_querysets_id": sheet_filter_querysets[4],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.5-Count of users by year.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Count of users by year</strong></span></p>""",
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
                "sheet_name": "Country Wise Users",
                "sheetfilter_querysets_id": sheet_filter_querysets[5],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.6-Country Wise Users.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Country Wise Users</strong></span></p>""",
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
                "sheet_name": "Salesforce Overview",
                "sheetfilter_querysets_id": sheet_filter_querysets[6],
                "datapath": os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'sheetdata', '7.7-Salesforce Overview.txt'),
                "datasrc": "",
                "sheet_tag_name": """<p style="text-align:center;"><span style="font-size:14px;"><strong>Salesforce Overview</strong></span></p>""",
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
            input_file_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'Dashboard-salesforce.txt')

            with open(input_file_path, 'r') as txt_file:
                data = json.load(txt_file)

            for index, item in enumerate(data):
                item['sheetId'] = sheet_ids_list[index]
                item['databaseId'] = hierarchy_id
                item['qrySetId'] = querysetid.queryset_id

            file_url, output_file_key = create_s3_file(input_file_path, sheet_ids_list, hierarchy_id, querysetid, bucket_name)

            image_image_path = os.path.join(BASE_DIR, 'dashboard', 'management', 'commands', 'dashboard', 'images', 'salesforce.jpeg')

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
            "height": "1700",
            "width": "800",
            "grid_id": 1,
            "role_ids": "",
            "user_ids": [],
            "dashboard_name": "Salesforce Analytics Dashboard",
            "datapath": output_file_key,
            "datasrc": file_url,
            "imagepath": output_image_key,
            "imagesrc": image_url,
            "dashboard_tag_name": """<p style="text-align:center;"><span style="font-size:16px;"><strong>Salesforce Analytics Dashboard&nbsp;</strong></span></p>""",
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