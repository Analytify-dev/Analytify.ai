import json
from django.core.management.base import BaseCommand
from dashboard import models
import datetime
from django.core.files.uploadedfile import InMemoryUploadedFile
import io, os
from project import settings


class Command(BaseCommand):
    help = 'Import JSON data into Django models'

    def handle(self, *args, **kwargs):
        # Load JSON data
        BASE_DIR = settings.BASE_DIR
        # Read the JSON data from the .txt file
        with open(os.path.join(BASE_DIR,'paths', 'defined.json')) as f:
            data = json.load(f)
        
        
            # Import Privileges
        if 'privileges' in data[0]:
            # models.previlages.objects.all().delete()  # Clear existing data
            privileges = data[0]['privileges']
            try:
                for priv in privileges:
                    
                    models.previlages.objects.update_or_create(id=priv['id'],
                        previlage=priv['privilege']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported Privileges'))
            except Exception as e:
                    self.stdout.write(self.style.WARNING(str(e)))
                    pass
            
        # Import Roles
        if 'roles' in data[1]:
            # models.Role.objects.all().delete()  # Clear existing data
            roles = data[1]['roles']
            try:
                for role in roles:
                
                    models.Role.objects.update_or_create(
                        role_id=role['role_id'],
                        role=role['role'],
                        # created_by="",
                        created_at=role['created_at'],
                        updated_at=role['updated_at'],
                        role_desc=role['role_desc'],
                        previlage_id = role['privilege_ids']
                        
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported Roles'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
            

        # Import FileTypes
        if 'file_types' in data[2]:
            # models.FileType.objects.all().delete()  # Clear existing data
            file_types = data[2]['file_types']
            try:
                for file_type in file_types:
                
                    models.FileType.objects.update_or_create(
                        id=file_type['id'],
                        file_type=file_type['file_type']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported FileTypes'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
            

        # Import ServerTypes
        if 'server_types' in data[3]:
            # models.ServerType.objects.all().delete()  # Clear existing data
            server_types = data[3]['server_types']
            try:
                for server_type in server_types:
                
                    models.ServerType.objects.update_or_create(
                        id=server_type['id'],
                        server_type=server_type['server_type']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported ServerTypes'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
            
        # Import GridTypes
        if 'grid_types' in data[4]:
            # models.grid_type.objects.all().delete()  # Clear existing data
            grid_types = data[4]['grid_types']
            try:
                for grid_type in grid_types:
                    models.grid_type.objects.update_or_create(
                        id=grid_type['id'],
                        grid_type=grid_type['grid_type']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported GridTypes'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
            
        # Import Charts
        if 'charts' in data[5]:
            # models.charts.objects.all().delete()  # Clear existing data
            charts = data[5]['charts']
            try:
                for chart in charts:
                    models.charts.objects.update_or_create(
                        id=chart['id'],
                        chart_type=chart['chart_type'],
                        min_measures=chart['min_measures'],
                        max_measures=chart['max_measures'],
                        min_dimensions=chart['min_dimensions'],
                        max_dimensions=chart['max_dimensions'],
                        min_dates=chart['min_dates'],
                        max_dates=chart['max_dates'],
                        min_geo=chart['min_geo'],
                        max_geo=chart['max_geo']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported Charts'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass

        # Import Modules (new index 6)
        if 'modules' in data[6]:
            # models.Module.objects.all().delete()  # Clear existing data
            modules = data[6]['modules']
            try:
                for module in modules:
                    models.Modules.objects.update_or_create(
                        id=module['id'],
                        module_name=module['module_name'],
                        angular_path=module['angular_path'],
                        css_classes=module['css_classes'],
                        image_urls=module['image_urls']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported Modules'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
        
        # Import User Guide (Index 7)
        if 'user_guide' in data[7]:
            user_guide = data[7]['user_guide']
            try:
                for guide in user_guide:
                    models.UserGuide.objects.update_or_create(
                        id=guide['id'],
                        title=guide['title'],
                        description=guide['description'],
                        link=guide['link'],
                        alias=guide['alias'],
                        # created_at=datetime.datetime.fromisoformat(guide['created_at'].replace("Z", "+00:00")),
                        # updated_at=datetime.datetime.fromisoformat(guide['updated_at'].replace("Z", "+00:00")),
                        module_id=models.Modules.objects.get(id = guide['module_id'])
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported User Guides'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(str(e)))
                pass
        # # Load the file content
        # with open('insightapps-sample', 'rb') as f:
        #     file_content = f.read()

        # # Create an InMemoryUploadedFile instance
        # file_obj = InMemoryUploadedFile(
        #     file=io.BytesIO(file_content),  # File content wrapped in BytesIO
        #     field_name='database_path',
        #     name='insightapps-sample',
        #     content_type='application/x-sqlite3',
        #     size=len(file_content),
        #     charset=None
        # )
        # try:
        #     models.ServerDetails.objects.create(
        #         id = 1,
        #         server_type = 4,
        #         user_id = 1,
        #         database_path = file_obj,
        #         display_name = 'example',
        #         is_connected = True,
        #         created_at = datetime.datetime.now(),
        #         updated_at = datetime.datetime.now()
        #     )
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Server Details'))
        # except:
        #     pass
        
        # querySetDefaultData={
        #     "queryset_id": 1,
        #     "user_id": 1,
        #     "server_id": 1,
        #     "file_id": "",
        #     "table_names": [["main", "employees", "employees"]],
        #     "join_type": [],
        #     "joining_conditions": [],
        #     "is_custom_sql": False,
        #     "custom_query": "SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\"",
        #     "query_name": "Employee Data",
        #     "created_at": datetime.datetime.now(),
        #     "updated_at": datetime.datetime.now(),
        #     "datasource_path": "insightapps/datasource/2024-08-29_12-26-13.txt",
        #     "datasource_json": "http://localhost:8000/media/insightapps/datasource/2024-08-29_12-26-13.txt"
        # }
        
        # # Convert lists and other non-string data to JSON strings
        # querySetDefaultData['table_names'] = json.dumps(querySetDefaultData['table_names'])
        # querySetDefaultData['join_type'] = json.dumps(querySetDefaultData['join_type'])
        # querySetDefaultData['joining_conditions'] = json.dumps(querySetDefaultData['joining_conditions'])

        # # Create and save the QuerySets instance
        # query_set_instance = models.QuerySets(
        #     queryset_id=querySetDefaultData["queryset_id"],
        #     user_id=querySetDefaultData["user_id"],
        #     server_id=querySetDefaultData["server_id"],
        #     file_id=querySetDefaultData["file_id"],
        #     table_names=querySetDefaultData["table_names"],
        #     join_type=querySetDefaultData["join_type"],
        #     joining_conditions=querySetDefaultData["joining_conditions"],
        #     is_custom_sql=querySetDefaultData["is_custom_sql"],
        #     custom_query=querySetDefaultData["custom_query"],
        #     query_name=querySetDefaultData["query_name"],
        #     created_at=querySetDefaultData["created_at"],
        #     updated_at=querySetDefaultData["updated_at"],
        #     datasource_path=querySetDefaultData["datasource_path"],
        #     datasource_json=querySetDefaultData["datasource_json"],
        # )

        # query_set_instance.save()
        # self.stdout.write(self.style.SUCCESS('Successfully imported data into QuerySet'))
        
        # sheetData=[
        #     {
        #         "id": 1,
        #         "user_id": 1,
        #         "chart_id": 25,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Employees Count",
        #         "sheet_filt_id": "1",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-31-03.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-31-03.txt",
        #         "sheet_tag_name": "Employees Count",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 2,
        #         "user_id": 1,
        #         "chart_id": 25,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [1],
        #         "sheet_name": "Female Employee Count",
        #         "sheet_filt_id": "2",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-33-58.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-33-58.txt",
        #         "sheet_tag_name": "Female Employee Count",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 3,
        #         "user_id": 1,
        #         "chart_id": 25,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [2],
        #         "sheet_name": "Male Employee Count",
        #         "sheet_filt_id": "3",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-34-59.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-34-59.txt",
        #         "sheet_tag_name": "Male Employee Count",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 4,
        #         "user_id": 1,
        #         "chart_id": 24,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Country wise Employee count",
        #         "sheet_filt_id": "4",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-43-39.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-43-39.txt",
        #         "sheet_tag_name": "Country wise Employee count",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 5,
        #         "user_id": 1,
        #         "chart_id": 6,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Average Annual Salary by Gender",
        #         "sheet_filt_id": "5",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-51-41.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-51-41.txt",
        #         "sheet_tag_name": "Average Annual Salary by Gende",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 6,
        #         "user_id": 1,
        #         "chart_id": 13,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Bonus Percentage Over Time",
        #         "sheet_filt_id": "6",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-54-30.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-54-30.txt",
        #         "sheet_tag_name": "Bonus Percentage Over Time",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 7,
        #         "user_id": 1,
        #         "chart_id": 24,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Gender Distribution",
        #         "sheet_filt_id": "7",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-54-59.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-54-59.txt",
        #         "sheet_tag_name": "Gender Distribution",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 8,
        #         "user_id": 1,
        #         "chart_id": 6,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Average Annual Salary by Department",
        #         "sheet_filt_id": "8",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-55-13.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-55-13.txt",
        #         "sheet_tag_name": "Average Annual Salary by Department",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 9,
        #         "user_id": 1,
        #         "chart_id": 10,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Number of Employees by Department",
        #         "sheet_filt_id": "9",
        #         "datapath": "insightapps/sheetdata/2024-08-29_12-57-44.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_12-57-44.txt",
        #         "sheet_tag_name": "Number of Employees by Department",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "id": 10,
        #         "user_id": 1,
        #         "chart_id": 1,
        #         "server_id": 1,
        #         "file_id": "",
        #         "queryset_id": 1,
        #         "filter_ids": [],
        #         "sheet_name": "Employee Details",
        #         "sheet_filt_id": "10",
        #         "datapath": "insightapps/sheetdata/2024-08-29_14-58-09.txt",
        #         "datasrc": "http://localhost:8000/media/insightapps/sheetdata/2024-08-29_14-58-09.txt",
        #         "sheet_tag_name": "Employee Details",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     }
        # ]
        # try:
        #     for data in sheetData:
        #         # Convert lists to JSON strings
        #         data['filter_ids'] = json.dumps(data['filter_ids'])
                
        #         # Create and save the sheet_data instance
        #         sheet_data_instance = models.sheet_data(
        #             id=data['id'],  # AutoField usually does not require setting manually, but including it for this example
        #             user_id=data['user_id'],
        #             chart_id=data['chart_id'],
        #             server_id=data['server_id'],
        #             file_id=data['file_id'],
        #             queryset_id=data['queryset_id'],
        #             filter_ids=data['filter_ids'],
        #             sheet_name=data['sheet_name'],
        #             sheet_filt_id=data['sheet_filt_id'],
        #             datapath=data['datapath'],  # Assuming the file already exists in the given path
        #             datasrc=data['datasrc'],
        #             sheet_tag_name=data['sheet_tag_name'],
        #             created_at=data['created_at'],
        #             updated_at=data['updated_at'],
        #         )
                
        #         sheet_data_instance.save()
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Sheet Data'))
        # except:
        #     pass
        
        # sheetFilterQuerySetData= [
        #     {
        #         "Sheetqueryset_id": 1,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": [],
        #         "rows": ["count(eeid)"],
        #         "custom_query": "SELECT COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 2,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [1],
        #         "columns": [],
        #         "rows": ["count(eeid)"],
        #         "custom_query": "SELECT COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table WHERE \"gender\" IN ('Female')",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 3,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [2],
        #         "columns": [],
        #         "rows": ["count(eeid)"],
        #         "custom_query": "SELECT COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table WHERE \"gender\" IN ('Male')",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 4,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["country"],
        #         "rows": ["count(eeid)"],
        #         "custom_query": "SELECT \"country\", COUNT(\"eeid\") AS \"count(eeid)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"country\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 5,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["gender"],
        #         "rows": ["avg(annual_salary)"],
        #         "custom_query": "SELECT \"gender\", AVG(\"annual_salary\") AS \"avg(annual_salary)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"gender\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 6,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["hire_date"],
        #         "rows": ["sum(bonus_percentage)"],
        #         "custom_query": "SELECT \"hire_date\", SUM(\"bonus_percentage\") AS \"sum(bonus_percentage)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"hire_date\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 7,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["gender"],
        #         "rows": ["count(gender)"],
        #         "custom_query": "SELECT \"gender\", COUNT(\"gender\") AS \"count(gender)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"gender\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 8,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["department"],
        #         "rows": ["avg(annual_salary)"],
        #         "custom_query": "SELECT \"department\", AVG(\"annual_salary\") AS \"avg(annual_salary)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"department\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 9,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["department"],
        #         "rows": ["count(department)"],
        #         "custom_query": "SELECT \"department\", COUNT(\"department\") AS \"count(department)\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"department\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #         "Sheetqueryset_id": 10,
        #         "datasource_querysetid": "",
        #         "queryset_id": "",
        #         "user_id": 4,
        #         "server_id": 1,
        #         "file_id": 1,
        #         "filter_id_list": [],
        #         "columns": ["eeid", "full_name", "job_title", "department", "business_unit", "gender", "ethnicity", "age", "hire_date", "annual_salary", "bonus_percentage", "country", "city"],
        #         "rows": [],
        #         "custom_query": "SELECT \"eeid\", \"full_name\", \"job_title\", \"department\", \"business_unit\", \"gender\", \"ethnicity\", \"age\", \"hire_date\", \"annual_salary\", \"bonus_percentage\", \"country\", \"city\" FROM (SELECT \"employees\".\"eeid\" AS \"eeid\", \"employees\".\"full_name\" AS \"full_name\", \"employees\".\"job_title\" AS \"job_title\", \"employees\".\"department\" AS \"department\", \"employees\".\"business_unit\" AS \"business_unit\", \"employees\".\"gender\" AS \"gender\", \"employees\".\"ethnicity\" AS \"ethnicity\", \"employees\".\"age\" AS \"age\", \"employees\".\"hire_date\" AS \"hire_date\", \"employees\".\"annual_salary\" AS \"annual_salary\", \"employees\".\"bonus_percentage\" AS \"bonus_percentage\", \"employees\".\"country\" AS \"country\", \"employees\".\"city\" AS \"city\" FROM \"main\".\"employees\" AS \"employees\") temp_table GROUP BY \"eeid\", \"full_name\", \"job_title\", \"department\", \"business_unit\", \"gender\", \"ethnicity\", \"age\", \"hire_date\", \"annual_salary\", \"bonus_percentage\", \"country\", \"city\"",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     }
        # ]
        # try:
        #     for entry in sheetFilterQuerySetData:
        #         # Create a new SheetFilter_querysets object
        #         models.SheetFilter_querysets.objects.create(
        #             Sheetqueryset_id=entry.get("Sheetqueryset_id"),
        #             datasource_querysetid=int(entry.get("datasource_querysetid") or 0) if entry.get("datasource_querysetid") else None,
        #             queryset_id=int(entry.get("queryset_id") or 0) if entry.get("queryset_id") else None,
        #             user_id=entry.get("user_id"),
        #             server_id=int(entry.get("server_id") or 0) if entry.get("server_id") else None,
        #             file_id=int(entry.get("file_id") or 0) if entry.get("file_id") else None,
        #             filter_id_list=json.dumps(entry.get("filter_id_list", [])),
        #             columns=json.dumps(entry.get("columns", [])),
        #             rows=json.dumps(entry.get("rows", [])),
        #             custom_query=entry.get("custom_query"),
        #             created_at=entry.get("created_at", datetime.datetime.now()),
        #             updated_at=entry.get("updated_at", datetime.datetime.now()),
        #         )
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into SheetFilter QuerySet'))
        # except:
        #     pass
        # chartFiltersData= [
        #     {
        #         "filter_id": 1,
        #         "user_id": 1,
        #         "server_id": 1,
        #         "file_id": "",
        #         "datasource_querysetid": "",
        #         "queryset_id": 1,
        #         "col_name": "gender",
        #         "data_type": "varchar",
        #         "filter_data": "('Female',)",
        #         "row_data": "('Female', 'Male')",
        #         "format_type": "%m/%d/%Y",
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #     },
        #     {
        #         "filter_id": 2,
        #         "user_id": 1,
        #         "server_id": 1,
        #         "file_id": "",
        #         "datasource_querysetid": "",
        #         "queryset_id": 1,
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
        #             filter_id=filter_data["filter_id"],
        #             user_id=filter_data["user_id"],
        #             server_id=filter_data["server_id"] or None,
        #             file_id=filter_data["file_id"] or None,
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
        # except:
        #     pass
        
        # dashbaordSampleData={
        #     "id": 1,
        #     "user_id": 1,
        #     "server_id": "",
        #     "queryset_id": "",
        #     "file_id": "",
        #     "sheet_ids": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        #     "selected_sheet_ids": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        #     "height": "1600",
        #     "width": "1025",
        #     "grid_id": 1,
        #     "role_ids": "",
        #     "user_ids": [],
        #     "dashboard_name": "Employee Sample Dashboard",
        #     "datapath": "insightapps/dashboard/2024-08-29_15-10-13.txt",
        #     "datasrc": "http://localhost:8000/media/insightapps/dashboard/2024-08-29_15-10-13.txt",
        #     "imagepath": "insightapps/dashboard/images/1724924426288.jpeg",
        #     "imagesrc": "http://localhost:8000/media/insightapps/dashboard/images/1724924426288.jpeg",
        #     "dashboard_tag_name": "Employee Sample Dashboard",
        #     "is_public": False,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        # }
        # try:
        #     dashboard_data_instance = models.dashboard_data(
        #         id=dashbaordSampleData["id"],
        #         user_id=dashbaordSampleData["user_id"],
        #         server_id=dashbaordSampleData["server_id"] or None,
        #         queryset_id=dashbaordSampleData["queryset_id"] or None,
        #         file_id=dashbaordSampleData["file_id"] or None,
        #         sheet_ids=','.join(map(str, dashbaordSampleData["sheet_ids"])),
        #         selected_sheet_ids=','.join(map(str, dashbaordSampleData["selected_sheet_ids"])),
        #         height=dashbaordSampleData["height"] or None,
        #         width=dashbaordSampleData["width"] or None,
        #         grid_id=dashbaordSampleData["grid_id"] or None,
        #         role_ids=dashbaordSampleData["role_ids"] or None,
        #         user_ids=','.join(map(str, dashbaordSampleData["user_ids"])),
        #         dashboard_name=dashbaordSampleData["dashboard_name"] or None,
        #         datapath=dashbaordSampleData["datapath"] or None,
        #         datasrc=dashbaordSampleData["datasrc"] or None,
        #         imagepath=dashbaordSampleData["imagepath"] or None,
        #         imagesrc=dashbaordSampleData["imagesrc"] or None,
        #         dashboard_tag_name=dashbaordSampleData["dashboard_tag_name"] or None,
        #         is_public=dashbaordSampleData["is_public"],
        #         created_at=datetime.datetime.now(),
        #         updated_at=datetime.datetime.now(),
        #     )

        #     dashboard_data_instance.save()
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashbaord Data'))
        # except:
        #     pass
        
        # dashbaordFiltersSampleData=[
        #         {
        #             "id": 1,
        #             "user_id": 1,
        #             "dashboard_id": 1,
        #             "sheet_id_list": [4, 5, 6, 7, 8, 9, 10],
        #             "filter_name": "Gender",
        #             "column_name": "gender",
        #             "column_datatype": "string",
        #             "queryset_id": 1,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #             "id": 2,
        #             "user_id": 1,
        #             "dashboard_id": 1,
        #             "sheet_id_list": [4, 5, 6, 7, 8, 9, 10],
        #             "filter_name": "Country",
        #             "column_name": "country",
        #             "column_datatype": "string",
        #             "queryset_id": 1,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #             "id": 3,
        #             "user_id": 1,
        #             "dashboard_id": 1,
        #             "sheet_id_list": [4, 5, 6, 7, 8, 9, 10],
        #             "filter_name": "Job Title",
        #             "column_name": "job_title",
        #             "column_datatype": "string",
        #             "queryset_id": 1,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #             "id": 4,
        #             "user_id": 1,
        #             "dashboard_id": 1,
        #             "sheet_id_list": [4, 5, 6, 7, 8, 9, 10],
        #             "filter_name": "Ethnicity",
        #             "column_name": "ethnicity",
        #             "column_datatype": "string",
        #             "queryset_id": 1,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         },
        #         {
        #             "id": 5,
        #             "user_id": 1,
        #             "dashboard_id": 1,
        #             "sheet_id_list": [4, 5, 6, 7, 8, 9, 10],
        #             "filter_name": "Bonus",
        #             "column_name": "bonus_percentage",
        #             "column_datatype": "string",
        #             "queryset_id": 1,
        #         "created_at":datetime.datetime.now(),
        #         "updated_at":datetime.datetime.now()
        #         }
        #     ]
        # try:
        #     for filter_data in dashbaordFiltersSampleData:
        #         models.DashboardFilters.objects.create(
        #             id=filter_data["id"],
        #             user_id=filter_data["user_id"],
        #             dashboard_id=filter_data["dashboard_id"],
        #             sheet_id_list=','.join(map(str, filter_data["sheet_id_list"])),
        #             filter_name=filter_data["filter_name"],
        #             column_name=filter_data["column_name"],
        #             column_datatype=filter_data["column_datatype"],
        #             queryset_id=filter_data["queryset_id"] or None,
        #             created_at=datetime.datetime.now(),
        #             updated_at=datetime.datetime.now(),
        #         )
            
        #     self.stdout.write(self.style.SUCCESS('Successfully imported data into Dashbaord Filter Data'))
        # except:
        #     pass