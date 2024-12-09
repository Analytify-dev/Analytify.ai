from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from dashboard.views import test_token
import psycopg2,cx_Oracle
from dashboard import models,serializers    
import pandas as pd
from sqlalchemy import text,inspect
import numpy as np
from .models import *
import ast,re,itertools
from datetime import datetime
import boto3
import json
import requests
from project import settings
import io
from dashboard.columns_extract import server_connection,query_filter,joining_sql,columns_first_data,custom_sql
from dashboard.Connections import file_save_1,litera_eval
from django.core.paginator import Paginator
import sqlglot
import logging
from dashboard import roles,previlages
from .Filters import connection_data_retrieve,server_details_check
from rest_framework.views import APIView

quotes = {
    'postgresql': ('"', '"'),
    'oracle': ('"', '"'),
    'mysql': ('`', '`'),
    'sqlite': ('"', '"'),
    'microsoftsqlserver': ('[', ']'),
    'snowflake': ('', '')
}
date_format_syntaxes = {
    'postgresql': lambda column: f"""to_char("{str(column)}", 'yyyy-mm-dd')""",
    'oracle': lambda column: f"""TO_CHAR("{str(column)}", 'YYYY-MM-DD')""",
    'mysql': lambda column: f"""DATE_FORMAT(`{str(column)}`, '%Y-%m-%d')""",
    'sqlite': lambda column: f"""strftime('%Y-%m-%d', "{str(column)}")""",
    'microsoftsqlserver': lambda column: f"""FORMAT([{str(column)}], 'yyyy-MM-dd')""",
    'snowflake': lambda column: f"""TO_CHAR({str(column)}, 'YYYY-MM-DD')"""
}


class DashboardQuerySetList(CreateAPIView):
    serializer_class = serializers.dashboard_querysetname_preview

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = tok1['user_id']
        dashboard_id = serializer.validated_data["dashboard_id"]
        if not dashboard_id:
            return Response({"message": "Dashboard ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not dashboard_data.objects.filter(id=dashboard_id).exists():
            return Response({"message": "Dashboard not found"}, status=status.HTTP_404_NOT_FOUND)

        dashboard = dashboard_data.objects.get(id=dashboard_id)
        
        queryset_ids1 = eval(dashboard.queryset_id)
        queryset_ids = list(set(queryset_ids1))
        sheet_ids = dashboard.sheet_ids
       
       
        data = []

        if isinstance(queryset_ids, str):
            try:
                queryset_ids = eval(queryset_ids)
            except (SyntaxError, NameError):
                return Response({"message": "Invalid queryset_ids format"}, status=status.HTTP_400_BAD_REQUEST)
                
        if isinstance(sheet_ids, str):
            try:
                sheet_ids = eval(sheet_ids)
            except (SyntaxError, NameError):
                return Response({"message": "Invalid sheet_ids format"}, status=status.HTTP_400_BAD_REQUEST)

        queryset_names = []

        for i in queryset_ids:
            try:

                m = QuerySets.objects.get(queryset_id=i).query_name
                queryset = QuerySets.objects.get(queryset_id=i)
                if queryset.server_id:   # Prefer server_id over file_id if available
                    db_name = ServerDetails.objects.get(id=queryset.server_id).display_name
                else:
                    db_name = FileDetails.objects.get(id = queryset.file_id).display_name

                queryset_names.append(m)
                data.append({
                    "dashboard_id": dashboard.id,
                    "queryset_id": i,
                    "queryset_name": m,
                    "database_name": db_name
                })
            except QuerySets.DoesNotExist:
                return Response({"message": f"QuerySet with id {i} not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(data, status=status.HTTP_200_OK)

# class DashboardQSColumnAndSheetsPreview(CreateAPIView):
#     serializer_class = serializers.DashboardpreviewSerializer

#     def post(self, request, token):
#         tok1 = test_token(token)
#         if tok1['status'] != 200:
#             return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = self.serializer_class(data=request.data)
#         if not serializer.is_valid():
#             return Response({'message': 'serializer error'}, status=status.HTTP_404_NOT_FOUND)
        
#         dashboard_id = serializer.validated_data["dashboard_id"]
#         query_id = serializer.validated_data["queryset_id"]
#         user_id = tok1['user_id']
#         existing_columns = []

#         if DashboardFilters.objects.filter(dashboard_id= dashboard_id,queryset_id = query_id).exists():
#             all_columns = DashboardFilters.objects.filter(dashboard_id= dashboard_id,queryset_id = query_id)
#             for i in all_columns:
#                 existing_columns.append(i.column_name)
#         else:
#             pass

#         if not dashboard_data.objects.filter(id=dashboard_id).exists():
#             return Response({'message': "Invalid Dashboard ID"}, status=status.HTTP_404_NOT_FOUND)
        
#         database_id,file_id,joining_tables,custom = get_server_id(query_id)
    
#         sheet_names = []

#         f = get_dashboard_sheets(dashboard_id,query_id)
#         for i in f:
#             sheet_names.append({"id": sheet_data.objects.get(id=i).id, "name": sheet_data.objects.get(id=i).sheet_name})
        
#         try:

#             con_data =connection_data_retrieve(database_id,file_id,user_id)
#             if joining_tables == "" or joining_tables == None:
#                 joining_tables = []
#             else:
#                 joining_tables = eval(joining_tables)
           
#             if con_data['status'] ==200:                
#                 ServerType1 = con_data['serverType1']
#                 server_details = con_data['server_details']
#                 file_type = con_data["file_type"]
#                 file_data =con_data["file_data"]
#                 dtype = con_data['dbtype']

#             else:
#                 return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
           
#             serdt=server_details_check(ServerType1,server_details,file_type,file_data,joining_tables,custom)
#             print(serdt)
#             if serdt['status']==200:
#                 print("hhhhhh")
#                 engine=serdt['engine']
#                 cursor=serdt['cursor']
#             else:
                
#                 return Response({'message':serdt['message']},status=serdt['status'])
#         except ServerDetails.DoesNotExist:
#             return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
#         except ServerType.DoesNotExist:
#             return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             print("llllllllllllllllllll")
#             qr = ''
#             # q_id = dashboard_data.objects.get(id=dashboard_id, user_id=user_id)
#             # query_id = q_id.queryset_id
#             joining = QuerySets.objects.get(queryset_id=query_id, user_id=user_id)
#             query_set = joining.custom_query
#             try:
#                 datasource_id = DataSource_querysets.objects.get(queryset_id=query_id, user_id=user_id)
#                 datasource_query = datasource_id.custom_query
#                 qr += datasource_query
#             except:
#                 qr += query_set
#             d = query_filter(qr,dtype)
#             print(d)
#             data = cursor.execute(text(qr))
            
#             if dtype.lower()== "microsoftsqlserver":
#                 samp = cursor.description
#                 columns_list = [
#                 {
#                     "column_name": col[0],
#                     "column_dtype": col[0].__name__
#                 }
#                 for col in samp
#             ]
#             else:
#                 samp = data.cursor.description
#                 type_code_to_name = get_columns_list(samp, dtype)
                    
#                 columns_list = [
#                     {
#                         "column_name": col[0],
#                         "column_dtype": type_code_to_name.get(col[1], 'string')
#                     }
#                     for col in samp
#                 ]
#             # print(columns_list,"!!!!!!!!")
#             columns_list = [col for col in columns_list if col['column_name'] not in existing_columns]

#             response_data = {
#                 "columns": columns_list,
#             }
#             return Response({"response_data": response_data, "sheets": sheet_names, "dashboard_id": dashboard_id, "server_id": database_id,"query_id":query_id}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

class DashboardQSColumnAndSheetsPreview(CreateAPIView):
    serializer_class = serializers.DashboardpreviewSerializer

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'serializer error'}, status=status.HTTP_404_NOT_FOUND)
        
        dashboard_id = serializer.validated_data["dashboard_id"]
        query_id = serializer.validated_data["queryset_id"]
        search = serializer.validated_data["search"]
        user_id = tok1['user_id']
        user_ids = dashboard_data.objects.get(id = dashboard_id)
        if str(user_id) in litera_eval(user_ids.user_ids):
            user_id = user_ids.user_id
        elif user_id == user_ids.user_id:
            user_id = user_id
        else:
            user_id = user_id

        if not dashboard_data.objects.filter(id=dashboard_id).exists():
            return Response({'message': "Invalid Dashboard ID"}, status=status.HTTP_404_NOT_FOUND)
        
        database_id, file_id, joining_tables, custom = get_server_id(query_id)
        if joining_tables == "" or joining_tables == None:
            joining_tables = []
    
        sheet_names = []
        f = get_dashboard_sheets(dashboard_id, query_id)

        for i in f:
            sheet_names.append({"id": sheet_data.objects.get(id=i, user_id=user_id).id, "name": sheet_data.objects.get(id=i, user_id=user_id).sheet_name})
        
        try:
            con_data = connection_data_retrieve(database_id, file_id, user_id)
            if con_data['status'] == 200:                
                ServerType1 = con_data['serverType1']
                server_details = con_data['server_details']
                file_type = con_data["file_type"]
                file_data = con_data["file_data"]
                dtype = con_data['dbtype']
            else:
                return Response({'message': con_data['message']}, status=status.HTTP_404_NOT_FOUND)

            serdt = server_details_check(ServerType1, server_details, file_type, file_data,ast.literal_eval(joining_tables),custom)
            if serdt['status'] == 200:
                engine = serdt['engine']
                cursor = serdt['cursor']
            else:
                return Response({'message': serdt['message']}, status=serdt['status'])
        except ServerDetails.DoesNotExist:
            return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
        except ServerType.DoesNotExist:
            return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qr = ''
            joining = QuerySets.objects.get(queryset_id=query_id, user_id=user_id)
            query_set = joining.custom_query
            try:
                datasource_id = DataSource_querysets.objects.get(queryset_id=query_id, user_id=user_id)
                datasource_query = datasource_id.custom_query
                qr2 = datasource_id
                qr += datasource_query
            except:
                qr2 = joining
                qr += query_set
            # Fetch data using the SQL query
            data = cursor.execute(text(qr))
            # Generate the SQL query result for `g`
            search1 = ''
            if dtype.lower() == "microsoftsqlserver":
                samp = cursor.description
                type_codes = [column[1] for column in samp]
                column_list = [column[0] for column in samp]
            else:
                type_codes = [column[1] for column in data.cursor.description]
                column_list = [column[0] for column in data.cursor.description]

            type_code_to_name = get_columns_list(data.cursor.description, dtype)
            data_types = None
            g = None
            if file_id:
                column_wise_first_record = columns_first_data(type_codes, data)
                if joining.is_custom_sql == True:
                    g=custom_sql(search,joining,column_wise_first_record,cursor,type_codes,column_list,file_data,file_id,query_id,data_types,user_id,parameter="file")
                else:
                    g = joining_sql(column_wise_first_record, search1, cursor, type_codes, engine, qr2, query_id, file_id, file_data, file_type.upper(), data_types,user_id, parameter="file")

            else:
                
                column_wise_first_record = columns_first_data(type_codes, data)
                if joining.is_custom_sql == True:
                    g=custom_sql(search,joining,column_wise_first_record,cursor,type_codes,column_list,server_details,file_id,query_id,data_types,user_id,parameter="file")
                    
                    
                else:
                    g = joining_sql(column_wise_first_record, search1, cursor, type_codes, engine, qr2, query_id, database_id, server_details, dtype.upper(), data_types,user_id, parameter=None)
            g = g.data
            
            table_wise_columns = {}

            for table_data in g:
                table_name = table_data.get('table_name')
                if not table_name:  # Check if table_name exists
                    continue
                if table_name == "public":  
                    continue
                if table_name not in table_wise_columns:
                    table_wise_columns[table_name] = []

                # Process dimensions
                for dim in table_data.get('dimensions', []):  # Use get to avoid KeyError
                    column_name = dim['column']
                    column_dtype = dim['data_type']
                    table_wise_columns[table_name].append({
                        "column_name": column_name,
                        "column_dtype": column_dtype
                    })

                # Print correctly accessed table columns

                # Process measures
                for meas in table_data.get('measures', []):  # Use get to avoid KeyError
                    column_name = meas['column']
                    column_dtype = meas['data_type']
                    table_wise_columns[table_name].append({
                        "column_name": column_name,
                        "column_dtype": column_dtype
                    })

            if search:
                table_wise_columns1 = search_columns(table_wise_columns, search)
                response_data = {
                    "tables": table_wise_columns1
                }
            else:
                response_data = {
                    "tables": table_wise_columns,
                }

            return Response({"response_data": response_data, "sheets": sheet_names, "dashboard_id": dashboard_id, "server_id": database_id, "query_id": query_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

     
def search_columns(data, search_query):
    search_query = search_query.lower().strip()
    tables = data
    result = {}
    for table_name, columns in tables.items():
        matching_columns = []
        for column in columns:
            column_name = column['column_name'].lower().strip()
            if search_query in column_name:
                matching_columns.append(column)
        if matching_columns:
            result[table_name] = matching_columns


    return result



        
def get_dashboard_sheets(dashboard_id, query_id):
    try:
        dd = dashboard_data.objects.get(id=dashboard_id)

        sheet_ids = []

        s = eval(dd.sheet_ids) if isinstance(dd.sheet_ids, str) else dd.sheet_ids
        
        for i in s:
            try:
                m = sheet_data.objects.get(id=i, queryset_id=query_id)
                sheet_ids.append(m.id)
            except sheet_data.DoesNotExist:
                continue
        return sheet_ids
    
    except dashboard_data.DoesNotExist:
        return Response({"message": "Invalid Dashboard ID"}, status=status.HTTP_404_NOT_FOUND)
        
class DashboardFilterSave(CreateAPIView):
    serializer_class = serializers.Dashboardfilter_save
    @transaction.atomic()
    def post(self, request, token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_dashboard_filter])
        tok1 = roles.role_status(token,role_list)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        
        dashboard_id = serializer.validated_data["dashboard_id"]
        filter_name = serializer.validated_data["filter_name"]
        table_name = serializer.validated_data["table_name"]
        selected_column = serializer.validated_data["column"]
        sheets = serializer.validated_data["sheets"]
        datatype = serializer.validated_data["datatype"]
        queryset_id = serializer.validated_data["queryset_id"]       
        user_id = tok1['user_id']
        user_ids = dashboard_data.objects.get(id = dashboard_id)
        if str(user_id) in litera_eval(user_ids.user_ids):
            user_id = user_ids.user_id
        elif user_id == user_ids.user_id:
            user_id = user_id
        else:
            user_id = user_id
        if DashboardFilters.objects.filter(dashboard_id=dashboard_id, filter_name=filter_name).exists():
            return Response(
                {"message": f"A filter with the name '{filter_name}' already exists for this dashboard."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if DashboardFilters.objects.filter(dashboard_id=dashboard_id, column_name=selected_column,queryset_id = queryset_id).exists():
            return Response(
                {"message": f"The column '{selected_column}' is already associated with this dashboard."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if dashboard_data.objects.filter(id = dashboard_id,user_id=user_id).exists():
           
            dash_filter = DashboardFilters.objects.create(
                user_id = user_id,
                dashboard_id = dashboard_id,
                sheet_id_list = sheets,
                filter_name = filter_name,
                table_name = table_name,
                column_name = selected_column,
                column_datatype = datatype,
                queryset_id = queryset_id
            )
            
            return Response({"dashboard_filter_id":dash_filter.id,
                            "dashboard_id":dashboard_id,
                            "filter_name":filter_name,
                            "table_name":table_name,
                            "selected_column":selected_column,
                            "sheets":sheets,
                            "datatype":datatype,
                            "queryset_id":queryset_id
                            })
        else:
            return Response({"message":"dashboard id not found"},status=status.HTTP_404_NOT_FOUND)
    
    serializer_get_clas = serializers.Dashboard_datapreviewSerializer
    def get(self,request,token):
        
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_get_clas(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        
        filter_id = serializer.validated_data["id"]
        user_id = tok1['user_id']
        if DashboardFilters.objects.filter(id= filter_id).exists():
            dash_filter = DashboardFilters.objects.get(id= filter_id,user_id = user_id)
            return Response({"dashboard_filter_id":dash_filter.id,
                                "dashboard_id":dash_filter.dashboard_id,
                                "filter_name":dash_filter.filter_name,
                                "table_name":dash_filter.table_name,
                                "selected_column":dash_filter.column_name,
                                "sheets":dash_filter.sheet_id_list,
                                "datatype":dash_filter.column_datatype
                                })
        else:
            return Response({"message":"dashboard filter id not found"},status=status.HTTP_404_NOT_FOUND)
        
    serializer_put_class = serializers.Dashboardfilter_save
    def put(self, request, token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_dashboard_filter])
        tok1 = roles.role_status(token,role_list)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_put_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        
        dashboard_filter_id = serializer.validated_data["dashboard_filter_id"]
        dashboard_id = serializer.validated_data["dashboard_id"]
        filter_name = serializer.validated_data["filter_name"]
        table_name = serializer.validated_data["table_name"]
        selected_column = serializer.validated_data["column"]
        sheets = serializer.validated_data["sheets"]
        datatype = serializer.validated_data["datatype"]
        queryset_id = serializer.validated_data["queryset_id"]       
        user_id = tok1['user_id']
        if not DashboardFilters.objects.filter(id = dashboard_filter_id).exists():
            return Response({"message":"dashboard filter id not found"},status=status.HTTP_404_NOT_FOUND)
        dashboard_filter = DashboardFilters.objects.get(id=dashboard_filter_id)

        # Check if the filter_name is being changed
        if dashboard_filter.filter_name != filter_name:
            # If filter_name is being changed, check if the new filter_name already exists
            if DashboardFilters.objects.filter(dashboard_id=dashboard_id, filter_name=filter_name).exists():
                return Response(
                    {"message": f"A filter with the name '{filter_name}' already exists for this dashboard."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Check if the selected_column is being changed
        if dashboard_filter.column_name != selected_column:
            # If column_name is being changed, check if the new column_name already exists
            if DashboardFilters.objects.filter(dashboard_id=dashboard_id, column_name=selected_column, queryset_id=queryset_id).exists():
                return Response(
                    {"message": f"The column '{selected_column}' is already associated with this dashboard."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        if dashboard_data.objects.filter(id = dashboard_id,user_id=user_id).exists():
            DashboardFilters.objects.filter(
                id = dashboard_filter_id
                ).update(
                user_id = user_id,
                dashboard_id = dashboard_id,
                sheet_id_list = sheets,
                filter_name = filter_name,
                table_name = table_name,
                column_name = selected_column,
                column_datatype = datatype,
                queryset_id = queryset_id,
                updated_at = datetime.now()
            )

            return Response({"dashboard_filter_id":dashboard_filter_id,
                            "dashboard_id":dashboard_id,
                            "filter_name":filter_name,
                            "table_name":table_name,
                            "selected_column":selected_column,
                            "sheets":sheets,
                            "datatype":datatype,
                            "queryset_id":queryset_id
                            })
        else:
            return Response({"message":"dashboard id not found"},status=status.HTTP_404_NOT_FOUND)
        


        
class DashboardFilterColumnDataPreview(CreateAPIView):
    serializer_class = serializers.Dashboard_datapreviewSerializer
    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status !=200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        filter_id = serializer.validated_data["id"]
        search_term = serializer.validated_data["search"]
        # user_id = tok1['user_id']
        if not DashboardFilters.objects.filter(id = filter_id).exists():
            return Response({'message':"Invalid Dashboard Filter ID"},status=status.HTTP_404_NOT_FOUND)
        
        if not dashboard_data.objects.filter(id = DashboardFilters.objects.get(id = filter_id).dashboard_id).exists():
            return Response({'message':"Invalid Dashboard ID"},status=status.HTTP_404_NOT_FOUND)
        query_id = DashboardFilters.objects.get(id = filter_id).queryset_id
        dashboard_id = DashboardFilters.objects.get(id = filter_id).dashboard_id
        database_id = get_server_id(query_id)
        column = DashboardFilters.objects.get(id = filter_id).column_name
        datatype = DashboardFilters.objects.get(id = filter_id).column_datatype
        database_id,file_id,joining_tables,custom = get_server_id(query_id)
        if joining_tables == "" or joining_tables == None:
                joining_tables = []
        else:
            pass
    

        dashboarddata=dashboard_data.objects.get(id=dashboard_id)

        if dashboarddata.is_public==True and token==None:
            user_id=dashboarddata.user_id
        elif dashboarddata.is_public==False and token==None:
            return Response({'message':'access token in needed'},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif dashboarddata.is_public==False and token!=None:
            user_id=dashboarddata.user_id
        else:
            user_id=tok1['user_id'] 

        try:
            con_data =connection_data_retrieve(database_id,file_id,user_id)
            if con_data['status'] ==200:                
                ServerType1 = con_data['serverType1']
                server_details = con_data['server_details']
                file_type = con_data["file_type"]
                file_data =con_data["file_data"]
                dtype = con_data['dbtype']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            
            serdt=server_details_check(ServerType1,server_details,file_type,file_data,eval(joining_tables),custom)
            if serdt['status']==200:
                engine=serdt['engine']
                cursor=serdt['cursor']
            else:
                return Response({'message':serdt['message']},status=serdt['status'])
            
        except ServerDetails.DoesNotExist:
            return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
        except ServerType.DoesNotExist:
            return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qr = ''
            # q_id = dashboard_data.objects.get(id=dashboard_id,user_id = user_id)
            # query_id = q_id.queryset_id
            joining= QuerySets.objects.get(queryset_id = query_id,user_id = user_id)
            query_set = joining.custom_query
            if DataSource_querysets.objects.filter(queryset_id = query_id,user_id = user_id).exists():
                datasource_id = DataSource_querysets.objects.get(queryset_id = query_id,user_id = user_id)
                datasource_query = datasource_id.custom_query
                qr += datasource_query
            else:
                qr += query_set
            if datatype in ["TIME","DATETIME","YEAR","TIMESTAMP","TIMESTAMPTZ","DATE","NUMERIC"]:
                col1 =date_format_syntaxes[dtype](column)
                col_query = "SELECT DISTINCT {} FROM ({})temp".format(col1,qr)
            else:
                col_query = "SELECT DISTINCT {} FROM ({})temp".format(quotes[dtype][0]+column+quotes[dtype][1],qr)
            col_query = convert_query(col_query,dtype)
          
            if dtype.lower() == "microsoftsqlserver":
                data = cursor.execute(str(col_query))
            elif dtype.lower() == "snowflake":
                col_query = col_query.replace('"', '')
                data = cursor.execute(text(col_query))
            else:
                data = cursor.execute(text(col_query))
            col = data.fetchall()
            col_data = [j for i in col for j in i]
            for i in col:
                for j in i:
                    d1 = j
                    col_data.append(d1)
            
            if search_term:
                col_data = [item for item in col_data if search_term.lower() in str(item).lower()]
            
            col_data = list(set(col_data))

            return Response({"col_data":col_data,"column_name":column}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND) 

        


class FinalDashboardFilterData(CreateAPIView):
    serializer_class = serializers.SheetDataSerializer

    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)

        filter_ids = serializer.validated_data["id"]
        input_lists = serializer.validated_data["input_list"]
        exclude_ids = serializer.validated_data["exclude_ids"]
         

        if len(filter_ids) != len(input_lists):
            return Response({'message': 'Filter IDs and input lists count mismatch'}, status=status.HTTP_400_BAD_REQUEST)
        

        # filter_ids = [fid for fid, il in zip(filter_ids, input_lists) if il]
        # input_lists = [il for il in input_lists if il]

        if not filter_ids or not input_lists:
            return Response({'message': 'No valid filters provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query_id = DashboardFilters.objects.get(id = filter_ids[0]).queryset_id
            dashboard_id = DashboardFilters.objects.get(id=filter_ids[0]).dashboard_id
            
        except DashboardFilters.DoesNotExist:
            return Response({'message': 'Invalid filter ID'}, status=status.HTTP_404_NOT_FOUND)
        except dashboard_data.DoesNotExist:
            return Response({'message': 'Invalid dashboard ID'}, status=status.HTTP_404_NOT_FOUND)

        dashboarddata=dashboard_data.objects.get(id=dashboard_id)
        if dashboarddata.is_public==True and token==None:
            user_id=dashboarddata.user_id
        elif dashboarddata.is_public==False and token==None:
            return Response({'message':'access token in needed'},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif dashboarddata.is_public==False and token!=None:
            user_id=dashboarddata.user_id
        else:
            user_id=tok1['user_id']    

        

        try:
            filter_details = []
            for filter_id in filter_ids:
                dash_filter = DashboardFilters.objects.get(id=filter_id,user_id=user_id)
                filter_details.append({
                    "filter_id": filter_id,
                    "dashboard_id": dash_filter.dashboard_id,
                    "sheet_list": eval(dash_filter.sheet_id_list),
                    "column_name": dash_filter.column_name,
                    "datatype": dash_filter.column_datatype,
                    "input_list": input_lists
                })
                
            sheet_ids = set()
            for filter_detail in filter_details:
                sheet_ids.update(filter_detail['sheet_list'])
            sheet_ids = list(sheet_ids)

            sheet_details = get_sheet_details(sheet_ids, user_id)
            sheet_mapping = {item["sheetfilter_queryset_id"]: item["sheet_id"] for item in sheet_details}
            sheetfilter_queryset_ids = [item["sheetfilter_queryset_id"] for item in sheet_details]

            details = []
            for sfid in sheetfilter_queryset_ids:
                try:
                    queryset_obj = SheetFilter_querysets.objects.get(Sheetqueryset_id=sfid,user_id = user_id)
                    sheet_id = sheet_mapping.get(sfid)
                    details.append({
                        "sheet_id": sheet_id,
                        "Sheetqueryset_id": queryset_obj.Sheetqueryset_id,
                        "query_id":queryset_obj.queryset_id,
                        "custom_query": queryset_obj.custom_query,
                        "columns": queryset_obj.columns,
                        "rows": queryset_obj.rows
                    })
                except Exception as e:
                    return Response(f'{e}', status=status.HTTP_404_NOT_FOUND)

            sql_queries = []
            for detail in details:
                custom_query = detail.get("custom_query", "")
                q_id = detail["query_id"]
                sheetq_id = detail["Sheetqueryset_id"]
                sheet1_id = detail["sheet_id"]
                
                where_clauses = []
                for i, filter_detail in enumerate(filter_details):
                    database_id,file_id,joining_tables,custom = get_server_id(int(q_id))
                    if joining_tables == "" or joining_tables == None:
                        joining_tables = []
                    else:
                        pass
                    try:
                        
                        con_data =connection_data_retrieve(database_id,file_id,user_id)
                        if con_data['status'] ==200:
                            ServerType1 = con_data['serverType1']
                            server_details = con_data['server_details']
                            file_type = con_data["file_type"]
                            file_data =con_data["file_data"]
                            dtype = con_data['dbtype']
                        
                        else:
                            return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                        serdt=server_details_check(ServerType1,server_details,file_type,file_data,eval(joining_tables),custom)
                        if serdt['status']==200:
                            engine=serdt['engine']
                            cursor=serdt['cursor']
                        else:
                            return Response({'message':serdt['message']},status=serdt['status'])
                    except ServerDetails.DoesNotExist:
                        return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
                    except ServerType.DoesNotExist:
                        return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    input_list = input_lists[i]
                    if input_list == []:  # Handle empty input_list case
                        # If input_list is empty, execute the original custom query without adding any conditions
                        final_query = custom_query.strip()

                        
                    if input_list != [] and sheet1_id in filter_detail["sheet_list"]:
                        column = filter_detail["column_name"]
                        # input_list = input_lists[i]
                        if isinstance(input_list, list) and all(isinstance(i, bool) for i in input_list):
                            if len(input_list) == 1:
                                input_list = f"({str(input_list[0]).lower()})"
                                where_clauses.append(f'"{column}" IN {input_list}')
                            elif set(input_list) == {False, True}:
                                input_list = "(true,false)"
                                where_clauses.append(f'"{column}" IN {input_list}')
                            else:
                                input_list = f"({','.join(str(x).lower() for x in input_list)})"
                                where_clauses.append(f'"{column}" IN {input_list}')

                        elif isinstance(input_list, bool):
                            input_list = f"({str(input_list).lower()})"
                      
                        elif filter_detail["datatype"] == "TIMESTAMPTZ" or filter_detail["datatype"] == 'TIMESTAMP'or filter_detail["datatype"] == 'DATE' :
                            f = transform_list(input_list)
                            formatted_list = tuple(f)
                            input1 = str(formatted_list).replace(',)', ')')
                            where_clauses.append(f"TO_CHAR(\"{column}\", 'YYYY-MM-DD') IN {input1}")
                        else:
                            try:
                               
                                formatted_list = tuple(item for item in input_list)
                            except ValueError:
                                f = transform_list(input_list)
                                formatted_list = tuple(f)
                            input1 = str(formatted_list).replace(',)', ')')
                            if int(filter_detail["filter_id"]) in exclude_ids:
                                where_clauses.append(f'"{column}" NOT IN {input1}')
                            else:
                                where_clauses.append(f'"{column}" IN {input1}')
                if where_clauses:
                    final_query = custom_query.strip()
                    
                    if 'GROUP BY' in final_query.upper():
                        parts = re.split(r'(\sGROUP\sBY\s)', final_query, flags=re.IGNORECASE)
                        main_query = parts[0]
                        group_by_clause = parts[1] + parts[2]
                    else:
                        main_query = final_query
                        group_by_clause = ''
                    
                    # Check if "temp1" is present in the query
                    if 'temp1' in main_query:
                        # Locate "temp_table" to apply the WHERE conditions after it
                        temp_table_end = main_query.rfind(') temp_table')
                        
                        if temp_table_end != -1:
                            before_temp_table = main_query[:temp_table_end + len(') temp_table')]
                            after_temp_table = main_query[temp_table_end + len(') temp_table'):]
                            
                            # Check if a WHERE clause is already present after temp_table
                            if 'WHERE' in after_temp_table.upper():
                                after_temp_table = re.sub(r'\sWHERE\s', ' WHERE ' + " AND ".join(where_clauses) + ' AND ', after_temp_table, flags=re.IGNORECASE)
                            else:
                                after_temp_table = " WHERE " + " AND ".join(where_clauses) + after_temp_table
                            
                            # Combine the parts
                            main_query = before_temp_table + after_temp_table
                        else:
                            # If temp_table is not found, keep original behavior
                            if 'WHERE' in main_query.upper():
                                main_query += " AND " + " AND ".join(where_clauses)
                            else:
                                main_query += " WHERE " + " AND ".join(where_clauses)
                    else:
                        # Original behavior for when "temp1" is not present
                        if 'WHERE' in main_query.upper():
                            main_query += " AND " + " AND ".join(where_clauses)
                        else:
                            main_query += " WHERE " + " AND ".join(where_clauses)
                    
                    # Combine the modified main query and the group by clause
                    final_query = main_query + " " + group_by_clause
                

                try:
                    dd = QuerySets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                    if DataSource_querysets.objects.filter(queryset_id = detail["query_id"],user_id=user_id).exists():
                        dd = DataSource_querysets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                    else:
                        pass
        
                    cleaned_query = re.sub(r'\(\s*SELECT[\s\S]+?\)\s*temp_table', '() temp_table', final_query, flags=re.IGNORECASE)
                    final_query = re.sub(r'\(\s*\)\s*temp_table', f"(\n{dd}\n) temp_table", cleaned_query)
                    final_query = convert_query(final_query, dtype.lower())
                    
                    colu = cursor.execute(text(final_query))
                    if dtype.lower() == "microsoftsqlserver":
                        colu = cursor.execute(str(final_query))
                        col_list = [column[0].replace(":OK",'') for column in cursor.description]
                    elif dtype.lower() == "snowflake":
                        colu = cursor.execute(text(final_query))
                        col_list = [column.replace(":OK",'') for column in colu.keys()]
                    else:
                        colu = cursor.execute(text(final_query))
             
                        col_list = [column.replace(":OK",'') for column in colu.keys()]
                    col_data = []
                    
                    for row in colu.fetchall():
                        col_data.append(list(row))
                    
                    a11 = []
                    rows11=[]
                    kk=ast.literal_eval(detail['columns'])
                    
                    for i in kk:
                        result = {}
                        
                        a = i.strip(' ')
                        a = a.replace('"',"")
                        
                        if a in col_list:
                            ind = col_list.index(a)

                            result['column'] = col_list[ind]
                            result['result'] = [item[ind] for item in col_data] 
                        a11.append(result)

                    
                    for i in ast.literal_eval(detail['rows']):
                        result1={}
                        a = i.strip(' ')
                        a =a.replace('"',"") 
                        if a in col_list:
                            ind = col_list.index(a)
                            result1['column'] = col_list[ind]
                            result1['result'] = [item[ind] for item in col_data]
                        rows11.append(result1)
                    
                    sheet_id11 = sheet_data.objects.get(id = sheet1_id,sheet_filt_id = sheetq_id)
                    sql_queries.append({
                        "sheet_id": sheet1_id,
                        "Sheetqueryset_id": sheetq_id,
                        "final_query": final_query,
                        "columns": a11,
                        "rows": rows11,
                        "queryset_id": query_id,
                        "chart_id":sheet_id11.chart_id
                    })
                except Exception as e:
                    return Response({'message': "Invalid Input Data for Column"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response(sql_queries, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
class Drill_through(CreateAPIView):
    serializer_class = serializers.dashboard_drill_through

    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)

        id = serializer.validated_data["drill_id"]
        dashboard_id = serializer.validated_data["dashboard_id"]
        # queryset_id = serializer.validated_data["queryset_id"]
        # main_sheet_id = serializer.validated_data["main_sheet_id"]
        # target_ids = serializer.validated_data["target_sheet_ids"]
        column_name = serializer.validated_data["column_name"]
        input_lists= serializer.validated_data["column_data"]
        data_type = serializer.validated_data["datatype"]
       

         

        dashboarddata=dashboard_data.objects.get(id=dashboard_id)
        if dashboarddata.is_public==True and token==None:
            user_id=dashboarddata.user_id
        elif dashboarddata.is_public==False and token==None:
            return Response({'message':'access token in needed'},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif dashboarddata.is_public==False and token!=None:
            user_id=dashboarddata.user_id
        else:
            user_id=tok1['user_id']    

        if Dashboard_drill_through.objects.filter(id=id).exists:
            drill_data = Dashboard_drill_through.objects.get(id=id,user_id=user_id)
            queryset_id = drill_data.queryset_id
            main_sheet_id = drill_data.source_sheet_id
            target_ids = eval(drill_data.target_sheet_id)
        else:
            return Response({"message":"drill_id does not exists"},status=status.HTTP_404_NOT_FOUND)
        
       
        try:
           
            sheet_ids = target_ids  
            sheet_details = get_sheet_details(sheet_ids, user_id)
            sheet_mapping = {item["sheetfilter_queryset_id"]: item["sheet_id"] for item in sheet_details}
            sheetfilter_queryset_ids = [item["sheetfilter_queryset_id"] for item in sheet_details]
            where_clauses = []
            details = []
            sql_queries = []
            processed_sheets = set()
            for sfid in sheetfilter_queryset_ids:
                try:
                    queryset_obj = SheetFilter_querysets.objects.get(Sheetqueryset_id=sfid,user_id = user_id)
                    sheet_id = sheet_mapping.get(sfid)
                    details.append({
                        "sheet_id": sheet_id,
                        "Sheetqueryset_id": queryset_obj.Sheetqueryset_id,
                        "query_id":queryset_obj.queryset_id,
                        "custom_query": queryset_obj.custom_query,
                        "columns": queryset_obj.columns,
                        "rows": queryset_obj.rows
                    })
                except Exception as e:
                    return Response(f'{e}', status=status.HTTP_404_NOT_FOUND)
            input_list = input_lists
            ##################################### for empty input ######################################
            if input_list == []: 
                
                for detail in details:
                    custom_query = detail.get("custom_query", "")
                    q_id = detail["query_id"]
                    sheetq_id = detail["Sheetqueryset_id"]
                    sheet1_id = detail["sheet_id"]
                   
                    final_query = custom_query.strip()
                    
                   
                    database_id,file_id,joining_tables,custom = get_server_id(int(q_id))
                    if joining_tables == "" or joining_tables == None:
                        joining_tables = []
                    else:
                        pass
                    try:
                        
                        con_data =connection_data_retrieve(database_id,file_id,user_id)
                        if con_data['status'] ==200:
                            ServerType1 = con_data['serverType1']
                            server_details = con_data['server_details']
                            file_type = con_data["file_type"]
                            file_data =con_data["file_data"]
                            dtype = con_data['dbtype']
                        
                        else:
                            return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                        serdt=server_details_check(ServerType1,server_details,file_type,file_data,eval(joining_tables),custom)
                        if serdt['status']==200:
                            engine=serdt['engine']
                            cursor=serdt['cursor']
                        else:
                            return Response({'message':serdt['message']},status=serdt['status'])
                    except ServerDetails.DoesNotExist:
                        return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
                    except ServerType.DoesNotExist:
                        return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
                    
                    try:
                    
                        dd = QuerySets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                        if DataSource_querysets.objects.filter(queryset_id = detail["query_id"],user_id=user_id).exists():
                            dd = DataSource_querysets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                        else:
                            pass
                        cleaned_query = re.sub(r'\(\s*SELECT[\s\S]+?\)\s*temp_table', '() temp_table', final_query, flags=re.IGNORECASE)
                        final_query2 = re.sub(r'\(\s*\)\s*temp_table', f"(\n{dd}\n) temp_table", cleaned_query)

                        final_query = convert_query(final_query2, dtype.lower())
                        
                        colu = cursor.execute(text(final_query))
                        if dtype.lower() == "microsoftsqlserver":
                            colu = cursor.execute(str(final_query))
                            col_list = [column[0].replace(":OK",'') for column in cursor.description]
                        elif dtype.lower() == "snowflake":
                            colu = cursor.execute(text(final_query))
                            col_list = [column.replace(":OK",'') for column in colu.keys()]
                        else:
                            colu = cursor.execute(text(final_query))
                
                            col_list = [column.replace(":OK",'') for column in colu.keys()]
                        col_data = []
                        
                        for row in colu.fetchall():
                            col_data.append(list(row))
                        a11 = []
                        rows11=[]
                        kk=ast.literal_eval(detail['columns'])
                        
                        for i in kk:
                            result = {}
                            
                            a = i.strip(' ')
                            a = a.replace('"',"")
                            
                            if a in col_list:
                                ind = col_list.index(a)

                                result['column'] = col_list[ind]
                                result['result'] = [item[ind] for item in col_data] 
                            a11.append(result)

                        
                        for i in ast.literal_eval(detail['rows']):
                            result1={}
                            a = i.strip(' ')
                            a =a.replace('"',"") 
                            if a in col_list:
                                ind = col_list.index(a)
                                result1['column'] = col_list[ind]
                                result1['result'] = [item[ind] for item in col_data]
                            rows11.append(result1)
                        sheet_id11 = sheet_data.objects.get(id =  detail["sheet_id"],sheet_filt_id = sheetq_id)
                        sql_queries.append({
                            "sheet_id": sheet1_id,
                            "Sheetqueryset_id": sheetq_id,
                            "final_query": final_query,
                            "columns": a11,
                            "rows": rows11,
                            "queryset_id": queryset_id,
                            "chart_id":sheet_id11.chart_id
                        })
                    except Exception as e:
                        return Response({'message': "Invalid Input Data for Column"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
                return Response(sql_queries, status=status.HTTP_200_OK)
        ################################ for non empty input ##############################
            else:
                for j in range(len(column_name)): 
                    if input_list != [] :
                        column = column_name[j]
                        input_list = input_lists[j]
                        datatype = data_type[j]
                        if isinstance(input_list, list) and all(isinstance(i, bool) for i in input_list):
                            if len(input_list) == 1:
                                input_list = f"({str(input_list[0]).lower()})"
                                where_clauses.append(f'"{column}" IN {input_list}')
                            elif set(input_list) == {False, True}:
                                input_list = "(true,false)"
                                where_clauses.append(f'"{column}" IN {input_list}')
                            else:
                                input_list = f"({','.join(str(x).lower() for x in input_list)})"
                                where_clauses.append(f'"{column}" IN {input_list}')

                        elif isinstance(input_list, bool):
                            input_list = f"({str(input_list).lower()})"
                    
                        elif datatype == "TIMESTAMPTZ" or datatype== 'TIMESTAMP'or datatype == 'DATE' :
                            f = transform_list(input_list)
                            formatted_list = tuple(f)
                            input1 = str(formatted_list).replace(',)', ')')
                            where_clauses.append(f"TO_CHAR(\"{column}\", 'YYYY-MM-DD') IN {input1}")
                        else:
                            try:
                            
                                formatted_list = tuple(item for item in input_list)
                            except ValueError:
                                f = transform_list(input_list)
                                formatted_list = tuple(f)
                            input1 = str(formatted_list).replace(',)', ')')
                        
                            where_clauses.append(f'"{column}" IN {input1}')
            
            for detail in details:
                custom_query = detail.get("custom_query", "")
                q_id = detail["query_id"]
                sheetq_id = detail["Sheetqueryset_id"]
                sheet1_id = detail["sheet_id"]
                
               
                for i in sheet_ids:
                    database_id,file_id,joining_tables,custom = get_server_id(int(q_id))
                    if joining_tables == "" or joining_tables == None:
                        joining_tables = []
                    else:
                        pass
                    try:
                        
                        con_data =connection_data_retrieve(database_id,file_id,user_id)
                        if con_data['status'] ==200:
                            ServerType1 = con_data['serverType1']
                            server_details = con_data['server_details']
                            file_type = con_data["file_type"]
                            file_data =con_data["file_data"]
                            dtype = con_data['dbtype']
                        
                        else:
                            return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                        serdt=server_details_check(ServerType1,server_details,file_type,file_data,eval(joining_tables),custom)
                        if serdt['status']==200:
                            engine=serdt['engine']
                            cursor=serdt['cursor']
                        else:
                            return Response({'message':serdt['message']},status=serdt['status'])
                    except ServerDetails.DoesNotExist:
                        return Response({'message': 'Server details not found'}, status=status.HTTP_404_NOT_FOUND)
                    except ServerType.DoesNotExist:
                        return Response({'message': 'Server type not found'}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                   
                if where_clauses:
                    final_query = custom_query.strip()
                    
                    if 'GROUP BY' in final_query.upper():
                        parts = re.split(r'(\sGROUP\sBY\s)', final_query, flags=re.IGNORECASE)
                        main_query = parts[0]
                        group_by_clause = parts[1] + parts[2]
                    else:
                        main_query = final_query
                        group_by_clause = ''
                    
                    # Check if "temp1" is present in the query
                    if 'temp1' in main_query:
                        # Locate "temp_table" to apply the WHERE conditions after it
                        temp_table_end = main_query.rfind(') temp_table')
                        
                        if temp_table_end != -1:
                            before_temp_table = main_query[:temp_table_end + len(') temp_table')]
                            after_temp_table = main_query[temp_table_end + len(') temp_table'):]
                            
                            # Check if a WHERE clause is already present after temp_table
                            if 'WHERE' in after_temp_table.upper():
                                after_temp_table = re.sub(r'\sWHERE\s', ' WHERE ' + " AND ".join(where_clauses) + ' AND ', after_temp_table, flags=re.IGNORECASE)
                            else:
                                after_temp_table = " WHERE " + " AND ".join(where_clauses) + after_temp_table
                            
                            # Combine the parts
                            main_query = before_temp_table + after_temp_table
                        else:
                            # If temp_table is not found, keep original behavior
                            if 'WHERE' in main_query.upper():
                                main_query += " AND " + " AND ".join(where_clauses)
                            else:
                                main_query += " WHERE " + " AND ".join(where_clauses)
                    else:
                        # Original behavior for when "temp1" is not present
                        if 'WHERE' in main_query.upper():
                            main_query += " AND " + " AND ".join(where_clauses)
                        else:
                            main_query += " WHERE " + " AND ".join(where_clauses)
                    
                    # Combine the modified main query and the group by clause
                    final_query = main_query + " " + group_by_clause
                

                try:
                   
                    dd = QuerySets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                    if DataSource_querysets.objects.filter(queryset_id = detail["query_id"],user_id=user_id).exists():
                        dd = DataSource_querysets.objects.get(queryset_id = detail["query_id"],user_id=user_id).custom_query
                    else:
                        pass
                    cleaned_query = re.sub(r'\(\s*SELECT[\s\S]+?\)\s*temp_table', '() temp_table', final_query, flags=re.IGNORECASE)
                    final_query2 = re.sub(r'\(\s*\)\s*temp_table', f"(\n{dd}\n) temp_table", cleaned_query)

                    final_query = convert_query(final_query2, dtype.lower())
                    
                    colu = cursor.execute(text(final_query))
                    if dtype.lower() == "microsoftsqlserver":
                        colu = cursor.execute(str(final_query))
                        col_list = [column[0].replace(":OK",'') for column in cursor.description]
                    elif dtype.lower() == "snowflake":
                        colu = cursor.execute(text(final_query))
                        col_list = [column.replace(":OK",'') for column in colu.keys()]
                    else:
                        colu = cursor.execute(text(final_query))
             
                        col_list = [column.replace(":OK",'') for column in colu.keys()]
                    col_data = []
                    
                    for row in colu.fetchall():
                        col_data.append(list(row))
                    a11 = []
                    rows11=[]
                    kk=ast.literal_eval(detail['columns'])
                    
                    for i in kk:
                        result = {}
                        
                        a = i.strip(' ')
                        a = a.replace('"',"")
                        
                        if a in col_list:
                            ind = col_list.index(a)

                            result['column'] = col_list[ind]
                            result['result'] = [item[ind] for item in col_data] 
                        a11.append(result)

                    
                    for i in ast.literal_eval(detail['rows']):
                        result1={}
                        a = i.strip(' ')
                        a =a.replace('"',"") 
                        if a in col_list:
                            ind = col_list.index(a)
                            result1['column'] = col_list[ind]
                            result1['result'] = [item[ind] for item in col_data]
                        rows11.append(result1)
                    
                    sheet_id11 = sheet_data.objects.get(id = sheet1_id,sheet_filt_id = sheetq_id)
                    sql_queries.append({
                        "sheet_id": sheet1_id,
                        "Sheetqueryset_id": sheetq_id,
                        "final_query": final_query,
                        "columns": a11,
                        "rows": rows11,
                        "queryset_id": queryset_id,
                        "chart_id":sheet_id11.chart_id
                    })
                except Exception as e:
                    return Response({'message': "Invalid Input Data for Column"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response(sql_queries, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)     
class Dashboard_drill_through_save(CreateAPIView):
    serializer_class = serializers.Drill_through_save
    @transaction.atomic()
    def post(self, request, token):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        
        action_name = serializer.validated_data["action_name"]
        dashboard_id = serializer.validated_data["dashboard_id"]
        queryset_id = serializer.validated_data["queryset_id"]
        main_sheet_id = serializer.validated_data["main_sheet_id"]
        target_sheet_ids = serializer.validated_data["target_sheet_ids"]
        user_id = tok1['user_id']
        user_ids = dashboard_data.objects.get(id = dashboard_id)
        if str(user_id) in litera_eval(user_ids.user_ids):
            user_id = user_ids.user_id
        elif user_id == user_ids.user_id:
            user_id = user_id
        else:
            user_id = user_id
        if Dashboard_drill_through.objects.filter(dashboard_id=dashboard_id, action_name = action_name).exists():
            return Response(
                {"message": f"Action with the name '{action_name}' already exists for this dashboard."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # if DashboardFilters.objects.filter(dashboard_id=dashboard_id, column_name=selected_column,queryset_id = queryset_id).exists():
        #     return Response(
        #         {"message": f"The column '{selected_column}' is already associated with this dashboard."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        if dashboard_data.objects.filter(id = dashboard_id,user_id=user_id).exists():
           
            dash_drill = Dashboard_drill_through.objects.create(
                user_id = user_id,
                action_name = action_name,
                queryset_id = queryset_id,
                dashboard_id = dashboard_id,
                source_sheet_id = main_sheet_id,
                target_sheet_id = target_sheet_ids
            )
            
            return Response({"dashboard_drill_thorugh_id":dash_drill.id,
                            "action_name":action_name,
                            "queryset_id":queryset_id,
                            "dashboard_id":dashboard_id,
                            "source_sheet_id":main_sheet_id,
                            "target_sheet_id":target_sheet_ids,
                            })
        else:
            return Response({"message":"dashboard id not found"},status=status.HTTP_404_NOT_FOUND)
        
    serializer_put_class = serializers.Drill_through_save
    def put(self, request, token):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_put_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        drill_through_id = serializer.validated_data["drill_through_id"]
        action_name = serializer.validated_data["action_name"]
        dashboard_id = serializer.validated_data["dashboard_id"]
        queryset_id = serializer.validated_data["queryset_id"]
        main_sheet_id = serializer.validated_data["main_sheet_id"]
        target_sheet_ids = serializer.validated_data["target_sheet_ids"]  
        user_id = tok1['user_id']
        if not Dashboard_drill_through.objects.filter(id = drill_through_id).exists():
            return Response({"message":"drill action  id not found"},status=status.HTTP_404_NOT_FOUND)
        drill_action = Dashboard_drill_through.objects.get(id=drill_through_id)

        # Check if action_name is being changed
        if drill_action.action_name != action_name:
            # If action_name is being changed, check if the new action_name already exists
            if Dashboard_drill_through.objects.filter(dashboard_id=dashboard_id, action_name=action_name).exists():
                return Response(
                    {"message": f"Action with the name '{action_name}' already exists for this dashboard."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # if Dashboard_drill_through.objects.filter(dashboard_id=dashboard_id, column_name=selected_column,queryset_id = queryset_id).exists():
        #     return Response(
        #         {"message": f"The column '{selected_column}' is already associated with this dashboard."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        
        if dashboard_data.objects.filter(id = dashboard_id,user_id=user_id).exists():
            Dashboard_drill_through.objects.filter(
                id = drill_through_id
                ).update(
                    user_id = user_id,
                    action_name = action_name,
                    queryset_id = queryset_id,
                    dashboard_id = dashboard_id,
                    source_sheet_id = main_sheet_id,
                    target_sheet_id = target_sheet_ids,
                    updated_at = datetime.now()
            )

            return Response({"dashboard_drill_thorugh_id":drill_through_id,
                            "action_name":action_name,
                            "queryset_id":queryset_id,
                            "dashboard_id":dashboard_id,
                            "source_sheet_id":main_sheet_id,
                            "target_sheet_id":target_sheet_ids,
                            })
        else:
            return Response({"message":"dashboard id not found"},status=status.HTTP_404_NOT_FOUND)
        
    serializer_get_clas = serializers.Drill_through_datapreview
    def get(self,request,token):
        
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_get_clas(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        
        id = serializer.validated_data["id"]
        user_id = tok1['user_id']
        if Dashboard_drill_through.objects.filter(id= id).exists():
            dash_drill = Dashboard_drill_through.objects.get(id= id,user_id = user_id)
            return Response({"drill_through_id":dash_drill.id,
                                "dashboard_id":dash_drill.dashboard_id,
                                "action_name":dash_drill.action_name,
                                "queryset_id":dash_drill.queryset_id,
                                "source_sheet_id":dash_drill.source_sheet_id,
                                "taret_sheet_ids":dash_drill.target_sheet_id
                               
                                })
        else:
            return Response({"message":"dashboard filter id not found"},status=status.HTTP_404_NOT_FOUND)
        
class Drill_through_get(CreateAPIView):
    def get(self, request, id, token):
        # Validate the token
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        # Get user ID from the token
        user_id = tok1['user_id']

        # Check if the drill-through action exists for the given ID and user
        try:
            dash_drill = Dashboard_drill_through.objects.get(id=id, user_id=user_id)
        except Dashboard_drill_through.DoesNotExist:
            return Response({"message": "Drill-through ID not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the response data
        data = {
            "drill_through_id": dash_drill.id,
            "dashboard_id": dash_drill.dashboard_id,
            "action_name": dash_drill.action_name,
            "queryset_id": dash_drill.queryset_id,
            "source_sheet_id": dash_drill.source_sheet_id,
            "target_sheet_ids": eval(dash_drill.target_sheet_id),  # Ensure `eval` is safe here
        }

        return Response(data, status=status.HTTP_200_OK)
    
class Drill_through_action_sheet_update(CreateAPIView):
    serializer_class = serializers.Drill_through_action_applied

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sheet_id = serializer.validated_data["sheet_id"]
        dashboard_id = serializer.validated_data["dashboard_id"]
        user_id = tok1['user_id']
        drill_data = Dashboard_drill_through.objects.filter(user_id = user_id,dashboard_id=dashboard_id)
        try:
            for action_id in drill_data:
                main_sheets = action_id.source_sheet_id
                target_sheets = eval(action_id.target_sheet_id)
                if sheet_id == main_sheets:
                    Dashboard_drill_through.objects.filter(id = action_id.id).delete()
                else:
                    if sheet_id in target_sheets:
                        target_sheets.remove(sheet_id)
                        if target_sheets == []:
                            Dashboard_drill_through.objects.filter(id = action_id.id).delete()
                        else:
                            Dashboard_drill_through.objects.filter(id = action_id.id).update(
                                                                user_id = user_id,
                                                                action_name = action_id.action_name,
                                                                queryset_id = action_id.queryset_id,
                                                                dashboard_id= action_id.dashboard_id,
                                                                source_sheet_id= action_id.source_sheet_id,
                                                                target_sheet_id = str(target_sheets),
                                                                updated_at = datetime.now())
                    else:
                        pass
                
            return Response(
                    {"message": "Actions related to this sheet will be altered."},
                    status=status.HTTP_200_OK
                )
        except Dashboard_drill_through.DoesNotExist:
            return Response(
                {"message": "Drill through data not found for the given user and dashboard."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class Drill_through_sheets(CreateAPIView):
    serializer_class = serializers.drill_through_sheets

    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)
        try:
            dashboard_id = serializer.validated_data["dashboard_id"]
            queryset_id = serializer.validated_data["queryset_id"]
            user_id = tok1['user_id']
            if not dashboard_id:
                return Response({"message": "Dashboard ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            if not dashboard_data.objects.filter(id=dashboard_id).exists():
                return Response({"message": "Dashboard not found"}, status=status.HTTP_404_NOT_FOUND)
            
            sheet_names = []
            f = get_dashboard_sheets(dashboard_id, queryset_id)

            for i in f:
                sheet_names.append({"id": sheet_data.objects.get(id=i, user_id=user_id).id, "name": sheet_data.objects.get(id=i, user_id=user_id).sheet_name})
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"sheet_data":sheet_names}, status=status.HTTP_200_OK)
    
class Drill_action_list(CreateAPIView):
    serializer_class = serializers.Drill_through_action_list

    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)

        dashboard_id = serializer.validated_data["dashboard_id"]
        user_id = tok1['user_id']

        data = []
        if Dashboard_drill_through.objects.filter(dashboard_id=dashboard_id,user_id = user_id).exists():
            dash_drill = Dashboard_drill_through.objects.filter(dashboard_id=dashboard_id,user_id = user_id)
            for i in dash_drill:
                data.append({
                    "drill_id": i.id,
                    "dashboard_id": i.dashboard_id,
                    "action_name": i.action_name,
                  
                })

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response([],status=status.HTTP_200_OK)
        

class Drill_through_action_details(CreateAPIView):
    serializer_class = serializers.Drill_through_action_details

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        id = serializer.validated_data["id"]
        user_id = tok1['user_id']
       
        if not Dashboard_drill_through.objects.filter(id=id).exists():
            return Response({"message": "drill action id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        dash_action = Dashboard_drill_through.objects.get(id=id)
        query_id = Dashboard_drill_through.objects.get(id = id).queryset_id
        queryname = QuerySets.objects.get(queryset_id = query_id).query_name
        
        dash_id = dash_action.dashboard_id
        main_sheet_id= Dashboard_drill_through.objects.get(id=id).source_sheet_id
        target_sheet_ids = eval(Dashboard_drill_through.objects.get(id=id).target_sheet_id)
        all_sheet_ids =eval(dashboard_data.objects.get(id=dash_id).sheet_ids)
        user_ids = dashboard_data.objects.get(id = dash_id)
        if str(user_id) in litera_eval(user_ids.user_ids):
            user_id = user_ids.user_id
        elif user_id == user_ids.user_id:
            user_id = user_id
        else:
            user_id = user_id
        dash_sheets = [
            sheet_id for sheet_id in all_sheet_ids
            if sheet_data.objects.filter(id=sheet_id, queryset_id=query_id).exists()
        ]
        # dash_filter.sheet_id_list = eval(dash_filter.sheet_id_list)
        source_sheets_data = [
            {
                "sheet_id": sheet_id,
                "sheet_name": sheet_data.objects.get(id=sheet_id).sheet_name,
                "selected": sheet_id == main_sheet_id
            }
            for sheet_id in all_sheet_ids
        ]
        sheets_data = [
            {
                "sheet_id": sheet_id,
                "sheet_name": sheet_data.objects.get(id=sheet_id).sheet_name,
                "selected": sheet_id in target_sheet_ids
            }
            for sheet_id in dash_sheets
        ]

        # Construct the response
        data = {
            "action_id": dash_action.id,
            "dashboard_id": dash_id,
            "action_name": dash_action.action_name,
            "main_sheet_data": source_sheets_data,
            "target_sheet_data": sheets_data,
            "queryname": queryname,
            "query_id": query_id,
        }

        return Response(data, status=status.HTTP_200_OK)
    
class Drill_through_delete(CreateAPIView):
    serializer_class = serializers.Drill_through_delete
    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        id = serializer.validated_data["id"]
        user_id = tok1['user_id']
        sheet_ids = []
        for fil in id:
            if Dashboard_drill_through.objects.filter(id=fil).exists():
                s = eval(Dashboard_drill_through.objects.get(id=fil,user_id=user_id).target_sheet_id)
                for i in s:
                    sheet_ids.append(i)
                Dashboard_drill_through.objects.get(id=fil,user_id=user_id).delete()
            else:
                return Response({"message": "Action ID not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Drill through Action Deleted Successfully","sheet_ids":sheet_ids},status=status.HTTP_200_OK)
    
class Drill_Noactionsheet(CreateAPIView):
    serializer_class = serializers.Drill_no_actionsheet

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = tok1['user_id']
        dashboard_id = serializer.validated_data["dashboard_id"]
        del_sheet_ids = serializer.validated_data["sheets_ids"]
        # saved_sheets = del_sheet_ids
        
        # filter_sheets = []
        # filter_ids = DashboardFilters.objects.filter(dashboard_id=dashboard_id,user_id=user_id)
        # sheet_ids = []

        # for filter_obj in filter_ids:
        #     sheet_ids.extend(ast.literal_eval(filter_obj.sheet_id_list))
        
        
        # remaining_sheets = [sheet for sheet in saved_sheets if sheet not in sheet_ids]
        sql_queries = []

        for s_id in del_sheet_ids:
            sheet_details = sheet_data.objects.get(id=s_id)
            sheet_query_id = int(sheet_details.sheet_filt_id)

            try:
                # Fetching server details
                sheetfilter = SheetFilter_querysets.objects.get(Sheetqueryset_id=sheet_query_id,user_id=user_id)
                query_id = sheet_details.queryset_id
                database_id, file_id, joining_tables, custom = get_server_id(int(query_id))
                if joining_tables == "" or joining_tables == None:
                    joining_tables = []
                else:
                    pass
                

                con_data = connection_data_retrieve(database_id, file_id, user_id)
                if con_data['status'] != 200:
                    return Response({'message': con_data['message']}, status=status.HTTP_404_NOT_FOUND)

                ServerType1 = con_data['serverType1']
                server_details = con_data['server_details']
                file_type = con_data["file_type"]
                file_data = con_data["file_data"]
                dtype = con_data['dbtype']

                serdt = server_details_check(ServerType1, server_details, file_type, file_data, eval(joining_tables), custom)
                if serdt['status'] != 200:
                    return Response({'message': serdt['message']}, status=serdt['status'])

                engine = serdt['engine']
                cursor = serdt['cursor']

                final_query = sheetfilter.custom_query
                final_query = convert_query(final_query, dtype.lower())

                if dtype.lower() == "microsoftsqlserver":
                    data = cursor.execute(str(final_query))
                else:
                    # final_query = final_query.replace('"', '') if dtype.lower() == "snowflake" else final_query
                    data = cursor.execute(text(final_query))

                col_list = [column.replace(":OK",'') for column in data.keys()]
                col_data = [list(row) for row in data.fetchall()]

                # Processing columns and rows
                columns_data = []
                rows_data = []

                for col_name in ast.literal_eval(sheetfilter.columns):
                    clean_col_name = col_name.strip(' ').replace('"', '')
                    if clean_col_name in col_list:
                        ind = col_list.index(clean_col_name)
                        columns_data.append({
                            "column": col_list[ind],
                            "result": [item[ind] for item in col_data]
                        })

                for row_name in ast.literal_eval(sheetfilter.rows):
                    clean_row_name = row_name.strip(' ').replace('"', '')
                    if clean_row_name in col_list:
                        ind = col_list.index(clean_row_name)
                        rows_data.append({
                            "column": col_list[ind],
                            "result": [item[ind] for item in col_data]
                        })

                sql_queries.append({
                    "sheet_id": s_id,
                    "Sheetqueryset_id": sheet_query_id,
                    "final_query": final_query,
                    "columns": columns_data,
                    "rows": rows_data,
                    "queryset_id": query_id,
                    "chart_id": sheet_details.chart_id
                })

            except (ServerDetails.DoesNotExist, ServerType.DoesNotExist):
                return Response({'message': 'Server details or server type not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(sql_queries, status=status.HTTP_200_OK)


        

###################################################################################################3
        
class Dashboard_filters_list(CreateAPIView):
    serializer_class = serializers.dashboard_filter_list

    def post(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            role_list = roles.get_previlage_id(previlage=[previlages.view_dashboard_filter,previlages.view_dashboard,previlages.edit_dasboard])
            tok1 = roles.role_status(token, role_list)
            tok_status=tok1['status']

        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)

        dashboard_id = serializer.validated_data["dashboard_id"]
        try:
            dashboard_sheets = eval(dashboard_data.objects.get(id=dashboard_id).sheet_ids)
        except :
            return Response([], status=status.HTTP_200_OK)

        data = []
        if DashboardFilters.objects.filter(dashboard_id=dashboard_id).exists():
            dash_filter = DashboardFilters.objects.filter(dashboard_id=dashboard_id)
            for i in dash_filter:
                data.append({
                    "dashboard_filter_id": i.id,
                    "dashboard_id": i.dashboard_id,
                    "filter_name": i.filter_name,
                    "table_name":i.table_name,
                    "selected_column": i.column_name,
                    "sheets": i.sheet_id_list,
                    "datatype": i.column_datatype
                })

            for filter_data in data:
                sheet_ids = eval(filter_data["sheets"])  # Convert string representation of list to actual list
                filter_data["sheet_counts"] = {}

                for sheet_id in dashboard_sheets:
                    count = sheet_ids.count(sheet_id)
                    filter_data["sheet_counts"][sheet_id] = count

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response([],status=status.HTTP_200_OK)



class DashboardFilterDetail(CreateAPIView):
    serializer_class = serializers.dashboard_filter_applied

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filter_id = serializer.validated_data["filter_id"]
        user_id = tok1['user_id']
        print(filter_id)
       
        if not DashboardFilters.objects.filter(id=filter_id).exists():
            return Response({"message": "Dashboard filter not found"}, status=status.HTTP_404_NOT_FOUND)
        
        dash_filter = DashboardFilters.objects.get(id=filter_id)
        query_id = DashboardFilters.objects.get(id = filter_id).queryset_id
        print(query_id)
        queryname = QuerySets.objects.get(queryset_id = query_id).query_name
        
        dash_id = dash_filter.dashboard_id
        dashboard = eval(dashboard_data.objects.get(id=dash_id).sheet_ids)
        all_sheet_ids = dashboard
        user_ids = dashboard_data.objects.get(id = dash_id)
        if str(user_id) in litera_eval(user_ids.user_ids):
            user_id = user_ids.user_id
        elif user_id == user_ids.user_id:
            user_id = user_id
        else:
            user_id = user_id
        dash_sheets = [
            sheet_id for sheet_id in all_sheet_ids
            if sheet_data.objects.filter(id=sheet_id, queryset_id=query_id).exists()
        ]
        dash_filter.sheet_id_list = eval(dash_filter.sheet_id_list)
        sheets_data = []
        for sheet_id in dash_sheets:
            sheet_name = sheet_data.objects.get(id=sheet_id).sheet_name
            sheets_data.append({
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
                "selected": sheet_id in dash_filter.sheet_id_list
            })
        
        data = {
            "dashboard_filter_id": dash_filter.id,
            "dashboard_id": dash_filter.dashboard_id,
            "filter_name": dash_filter.filter_name,
            "table_name":dash_filter.table_name,
            "selected_column": dash_filter.column_name,
            "sheets": sheets_data,
            "queryname": queryname,
            "query_id": query_id,
            "datatype": dash_filter.column_datatype
        }
        
        return Response(data, status=status.HTTP_200_OK)
    
class Nofiltersheet(CreateAPIView):
    serializer_class = serializers.dashboard_nosheet_data

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = tok1['user_id']
        dashboard_id = serializer.validated_data["dashboard_id"]
        del_sheet_ids = serializer.validated_data["sheet_ids"]
        saved_sheets = del_sheet_ids
        
        filter_sheets = []
        filter_ids = DashboardFilters.objects.filter(dashboard_id=dashboard_id,user_id=user_id)
        sheet_ids = []

        for filter_obj in filter_ids:
            sheet_ids.extend(ast.literal_eval(filter_obj.sheet_id_list))
        
        
        remaining_sheets = [sheet for sheet in saved_sheets if sheet not in sheet_ids]
        sql_queries = []

        for s_id in remaining_sheets:
            sheet_details = sheet_data.objects.get(id=s_id)
            sheet_query_id = int(sheet_details.sheet_filt_id)

            try:
                # Fetching server details
                sheetfilter = SheetFilter_querysets.objects.get(Sheetqueryset_id=sheet_query_id,user_id=user_id)
                query_id = sheet_details.queryset_id
                database_id, file_id, joining_tables, custom = get_server_id(int(query_id))
                if joining_tables == "" or joining_tables == None:
                    joining_tables = []
                else:
                    pass
                

                con_data = connection_data_retrieve(database_id, file_id, user_id)
                if con_data['status'] != 200:
                    return Response({'message': con_data['message']}, status=status.HTTP_404_NOT_FOUND)

                ServerType1 = con_data['serverType1']
                server_details = con_data['server_details']
                file_type = con_data["file_type"]
                file_data = con_data["file_data"]
                dtype = con_data['dbtype']

                serdt = server_details_check(ServerType1, server_details, file_type, file_data, eval(joining_tables), custom)
                if serdt['status'] != 200:
                    return Response({'message': serdt['message']}, status=serdt['status'])

                engine = serdt['engine']
                cursor = serdt['cursor']

                final_query = sheetfilter.custom_query
                final_query = convert_query(final_query, dtype.lower())

                if dtype.lower() == "microsoftsqlserver":
                    data = cursor.execute(str(final_query))
                else:
                    # final_query = final_query.replace('"', '') if dtype.lower() == "snowflake" else final_query
                    data = cursor.execute(text(final_query))

                col_list = [column.replace(":OK",'') for column in data.keys()]
                col_data = [list(row) for row in data.fetchall()]

                # Processing columns and rows
                columns_data = []
                rows_data = []

                for col_name in ast.literal_eval(sheetfilter.columns):
                    clean_col_name = col_name.strip(' ').replace('"', '')
                    if clean_col_name in col_list:
                        ind = col_list.index(clean_col_name)
                        columns_data.append({
                            "column": col_list[ind],
                            "result": [item[ind] for item in col_data]
                        })

                for row_name in ast.literal_eval(sheetfilter.rows):
                    clean_row_name = row_name.strip(' ').replace('"', '')
                    if clean_row_name in col_list:
                        ind = col_list.index(clean_row_name)
                        rows_data.append({
                            "column": col_list[ind],
                            "result": [item[ind] for item in col_data]
                        })

                sql_queries.append({
                    "sheet_id": s_id,
                    "Sheetqueryset_id": sheet_query_id,
                    "final_query": final_query,
                    "columns": columns_data,
                    "rows": rows_data,
                    "queryset_id": query_id,
                    "chart_id": sheet_details.chart_id
                })

            except (ServerDetails.DoesNotExist, ServerType.DoesNotExist):
                return Response({'message': 'Server details or server type not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"sql_queries": sql_queries}, status=status.HTTP_200_OK)


    

    
class DashboardFilterDelete(CreateAPIView):
    serializer_class = serializers.dashboard_filter_delete
    def post(self, request, token):
        role_list=roles.get_previlage_id(previlage=[previlages.delete_dashboard_filter])
        tok1 = roles.role_status(token,role_list)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        filter_ids = serializer.validated_data["filter_id"]
        user_id = tok1['user_id']
        sheet_ids = []
        for fil in filter_ids:
            if DashboardFilters.objects.filter(id=fil).exists():
                s = eval(DashboardFilters.objects.get(id=fil,user_id=user_id).sheet_id_list)
                for i in s:
                    sheet_ids.append(i)
                DashboardFilters.objects.get(id=fil,user_id=user_id).delete()
            else:
                return Response({"message": "Dashboard filter ID not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Filter Deleted Successfully","sheet_ids":sheet_ids},status=status.HTTP_200_OK)


class Dashboard_filtersheet_update(CreateAPIView):
    serializer_class = serializers.dashboard_filtersheet
    
    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dashboard_id = serializer.validated_data["dashboard_id"]
        update_sheet_ids = serializer.validated_data["sheet_ids"]
        
        try:
            dash_filters = DashboardFilters.objects.filter(dashboard_id=dashboard_id)
            for fil in dash_filters:
                filter_sheet = eval(fil.sheet_id_list)
                filter_sheets = list(filter_sheet)

                
                if update_sheet_ids in filter_sheets:
                    filter_sheets.remove(update_sheet_ids)
                if not filter_sheets:  # If filter_sheets is empty
                    DashboardFilters.objects.filter(id=fil.id).delete()
                else:
                    DashboardFilters.objects.filter(
                        id=fil.id
                    ).update(
                        user_id=fil.user_id,
                        dashboard_id=fil.dashboard_id,
                        sheet_id_list=filter_sheets,
                        table_name = fil.table_name,
                        filter_name=fil.filter_name,
                        column_name=fil.column_name,
                        column_datatype=fil.column_datatype,
                        queryset_id=fil.queryset_id,
                        updated_at=datetime.now()
                    )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Filters Updated Successfully for sheet f{}".format(sheet_data.objects.get(id=update_sheet_ids).sheet_name)}, status=status.HTTP_200_OK)

        

    
class Dashboard_sheet_update(CreateAPIView):
    serializer_class = serializers.dashboard_chartsheet_update

    def post(self, request, token):
        
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        sheet_id = serializer.validated_data['sheet_id']
        user_id = tok1['user_id']

        if not sheet_id:
            return Response({"message": "sheet_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if sheet_id exists in any dashboard's sheet_ids
        dashboards = dashboard_data.objects.filter(sheet_ids__contains=str(sheet_id), user_id=user_id)
        if not dashboards.exists():
            return Response({"message": "sheet_id not found in any dashboard"}, status=status.HTTP_404_NOT_FOUND)

        # Initialize variables for each chart type and data
        sheet_data_dict = {}
        

        try:
            # Retrieve the sheet data
            sheet = sheet_data.objects.get(id=sheet_id)
            data_sources = sheet.datasrc
            chart_id = int(sheet.chart_id)
            chart_type = charts.objects.get(id=chart_id).chart_type
            response = requests.get(data_sources)
            sheet_data_json = response.json()
            sheet_name = sheet.sheet_name
            sheet_tag_name = sheet.sheet_tag_name
            echart =  sheet_data_json.get("isEChart")
            number_format = sheet_data_json.get("numberFormat")
           

            if chart_id == 1:  # Table chart
                table = sheet_data_json.get("results", {})
                
                banding = table.get("banding")
                
                table_data = table.get("tableData", [])  
                table_columns = table.get("tableColumns", [])
                customizeOptions = sheet_data_json.get('customizeOptions')
                if table.get("color1") or table.get("color2"):
                    color1 = table.get("color1")
                    sheet_data_dict[sheet_id] = {
                    'chartType': chart_type,
                    'sheetTagName': sheet_tag_name,
                    'sheetName': sheet_name,
                    'customizeOptions':customizeOptions,
                    'tableData': {
                        'headers': table_columns,
                        'rows': table_data,
                        'banding':banding,
                        'color1': table.get("color1"),
                        'color2': table.get("color2")
                    }
                    }
                else:
                
                    sheet_data_dict[sheet_id] = {
                        'chartType': chart_type,
                        'sheetTagName': sheet_tag_name,
                        'sheetName': sheet_name,
                        'customizeOptions':customizeOptions,
                        'tableData': {
                            'headers': table_columns,
                            'rows': table_data,
                            'banding':banding
                        }
                    }
            elif chart_id == 25:  # KPI chart
                kpi_table = sheet_data_json.get("results", {})
                kpi_data = kpi_table.get("kpiData")
                kpi_font = kpi_table.get("kpiFontSize")
                kpi_col = kpi_table.get("kpicolor")
                kpi_num = kpi_table.get("kpiNumber")
                kpi_prefix = kpi_table.get("kpiPrefix")
                kpi_sufix = kpi_table.get("kpiSuffix")
                sheet_data_dict[sheet_id] = {
                    'chartType': chart_type,
                    'sheetName':sheet_name,
                    'sheetTagName': sheet_tag_name,
                    'kpiData': {
                        'kpiNumber': kpi_num,
                        'kpiPrefix':kpi_prefix,
                        'kpiSuffix':kpi_sufix,
                        'rows': kpi_data,
                        'fontSize': kpi_font,
                        'color': kpi_col
                    },
                    
                }
            else:  # Other chart types
                results = sheet_data_json.get("savedChartOptions", {})
                columns_data = sheet_data_json.get("columns_data",{})

                rows_data = sheet_data_json.get("rows_data",{})

                sheet_data_dict[sheet_id] = {
                    'chartType': chart_type,
                    'sheetName':sheet_name,
                    'sheetTagName': sheet_tag_name,
                    'chartOptions': results,
                    'columns_data':columns_data,
                    'rows_data':rows_data
                    # 'numberFormat':number_format
                }

        except sheet_data.DoesNotExist:
            return Response({"message": f"Sheet data not found for id {sheet_id}"}, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"message": f"Error fetching sheet data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # For each dashboard where the sheet_id is present, update the data
        
        try:
            for dashboard in dashboards:
                dashboard_datasrc = dashboard.datasrc
                response2 = requests.get(dashboard_datasrc)
                dash_data = response2.json()

                for a in dash_data:
                    if a.get('sheetId') == sheet_id:
                        sheet_info = sheet_data_dict[sheet_id]

                        # Handle Table chart
                        if sheet_info['chartType'] == 'Table':
                
                            if 'chartOptions' in a:
                                a['chartOptions'] = {}
                            a['tableData'] = sheet_info.get('tableData', {})
                            a['chartId'] = chart_id
                            a["data"]["title"] = sheet_info.get('sheetName')
                            a["data"]["sheetTagName"] = sheet_info.get('sheetTagName')
                            a["customizeOptions"] = sheet_info.get('customizeOptions')
                           
                            if echart == True :
                                
                                a["isEChart"] = False
                            else:
                                pass

                        # Handle KPI chart
                        elif sheet_info['chartType'] == 'KPI':
                            if 'tableData' in a:
                                del a['tableData']
                            if 'chartOptions' in a:
                                del a['chartOptions']
                            a['chartId'] = chart_id
                            a['kpiData'] = sheet_info.get('kpiData', {})
                            
                            a["data"]["title"] = sheet_info.get('sheetName')
                            a["data"]["sheetTagName"] = sheet_info.get('sheetTagName')

                        # Handle other chart types
                        else:
                            if 'tableData' in a:
                                del a['tableData']
                            if 'kpiData' in a:
                                del a['kpiData']
                            if echart == True:
                                a['echartOptions'] = sheet_info.get('chartOptions', {})
                                a['isEChart'] = echart
                                
                            else:
                                a['chartOptions'] = sheet_info.get('chartOptions', {})
                                a['isEChart'] = echart
                        a['chartType'] = sheet_info['chartType']
                        a['chartId'] = chart_id
                        try:
                            if a['numberFormat']:
                                a['numberFormat'] = number_format
                        except:
                            pass
                        a["data"]["title"] = sheet_info.get('sheetName')
                        a["data"]["sheetTagName"] = sheet_info.get('sheetTagName')
                        a["column_Data"] = sheet_info.get('columns_data')
                        a["row_Data"] = sheet_info.get('rows_data')

              
                server_id = None
                queryset_id = None
                filesave = file_save_1(dash_data, server_id, queryset_id, ip='dashboard', dl_key=dashboard.datapath)
                dashboard_data.objects.filter(id=dashboard.id).update(datasrc=filesave['file_url'], datapath=filesave['file_key'])

        except dashboard_data.DoesNotExist:
            return Response({"message": "Dashboard data source not found"}, status=status.HTTP_404_NOT_FOUND)
        except requests.RequestException as e:
            return Response({"message": f"Error fetching dashboard data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Sheet data updated successfully","dash_data":dash_data}, status=status.HTTP_200_OK) 





class userguide_function(CreateAPIView):
    serializer_class = serializers.user_guide_serializer
    
    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        module_id = serializer.validated_data["module_id"]
        slug = serializer.validated_data["slug"]

        try:
            user_data = []
            angular_path = None
            
            if module_id not in (None,"",0):
                user_data = UserGuide.objects.filter(module_id=module_id).values()
                
                angular_path = Modules.objects.get(id=module_id).angular_path
                
                return Response({"user_guide_data": list(user_data), "angular_path": angular_path}, status=status.HTTP_200_OK)
            
          
            if slug:
                user_data1 =[]
                user_data = UserGuide.objects.get(alias=slug)
                mod_id = user_data.module_id.id
                user_data1.append({
                    "title":user_data.title,
                    "description":user_data.description,
                    "link":user_data.link,
                    "module_id":mod_id,
                    "alias":user_data.alias
                })
                
                angular_path = Modules.objects.get(id=mod_id).angular_path
                
                return Response({"user_guide_data": user_data1, "angular_path": angular_path}, status=status.HTTP_200_OK)
            
            return Response({"message": "Please provide either a valid module_id or slug."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class userguide_search(CreateAPIView):
    serializer_class = serializers.userguide_search_serializer

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        search = serializer.validated_data["search"]

        try:
            # Perform search in UserGuide table, looking for matches in title, description, and alias fields
            user_data = list(
                UserGuide.objects.filter(title__icontains=search).values() |
                UserGuide.objects.filter(description__icontains=search).values() |
                UserGuide.objects.filter(alias__icontains=search).values()
            )
            
            if not user_data:
                return Response({"message": "No matching user guide records found."}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({"user_guide_data": user_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ListModuleDataView(APIView):
    def get(self, request, token):
        # Validate the token
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        # Fetch module data
        module_data = Modules.objects.all().values()

        # Return response
        return Response({'data': list(module_data)}, status=status.HTTP_200_OK)
    

class User_Configuration(CreateAPIView):
    serializer_class = serializers.user_configuration_serializer

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        chart_type = serializer.validated_data["chart_type"]
        
        try:
            user_config, created = UserConfigurations.objects.update_or_create(
                user_id=user_id, 
                defaults={"chart_type": chart_type}
            )
            
            if created:
                message = "User configuration created successfully."
            else:
                message = "User configuration updated successfully."
            
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request,token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        if not user_id:
            return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_config = UserConfigurations.objects.get(user_id=user_id)
            
            if user_config:
                data = {
                    "user_id": user_config.user_id,
                    "chart_type": user_config.chart_type
                }
                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User id from User configuration not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


###########################################################################  api functions ###########################################################

def transform_list(data):
    transformed_data = []
    for element in data:
        if isinstance(element, list):
            if len(element) == 1 and isinstance(element[0], str) and ',' in element[0]:
                transformed_element = element[0]
            else:
                transformed_element = "'" + "','".join(element) + "'"
        else:
            transformed_element = element
        
        transformed_data.append(transformed_element)

    return transformed_data

def get_sheet_details(sheet_ids, user_id):
    details = []

    for sheet_id in sheet_ids:
        try:
            sheet_data_obj = sheet_data.objects.get(id=sheet_id, user_id=user_id)
            sheetfilter_queryset_id = sheet_data_obj.sheet_filt_id
            chart_id = sheet_data_obj.chart_id
            sheet_data_source = sheet_data_obj.datasrc
            queryset_id = sheet_data_obj.queryset_id

            details.append({
                "sheet_id": sheet_id,
                "chart_id": chart_id,
                "sheetfilter_queryset_id": sheetfilter_queryset_id,
                "sheet_data_source": sheet_data_source,
                "queryset_id": queryset_id
            })
        except sheet_data.DoesNotExist:
            raise Exception(f"sheet_data with id {sheet_id} and user_id {user_id} does not exist.")

    return details

def convert_query(query,dtype):
 
    a = {'postgresql':'postgres','oracle':'oracle','mysql':'mysql','sqlite':'sqlite','microsoftsqlserver':'tsql','snowflake':'snowflake'}
    if a[dtype]:
        res = a[dtype]

    else:
        res = 'invalid datatype'
    try:
        parsed_query = sqlglot.parse_one(query,read=res)
        converted_query = parsed_query.sql(dialect=res)
    except Exception as e:
        print(str(e),"YYYYYYYYYYYYY")
    

    return converted_query

def get_server_id(query_id):
    try:
        q_id = QuerySets.objects.get(queryset_id=query_id)
        # server_id = eval(q_id.server_id)
        # file_id = eval(q_id.file_id)
        # joining_tables = eval(q_id.table_names)
        # print(q_id.server_id,q_id.file_id,q_id.table_names,q_id.is_custom_sql)
        return q_id.server_id,q_id.file_id,q_id.table_names,q_id.is_custom_sql
        
    except dashboard_data.DoesNotExist:
        return None

def get_columns_list(samp, server_type):

    postgres_type_code_to_name = {
        16: 'BOOLEAN',
        20: 'BIGINT',
        23: 'INTEGER',
        1042: 'CHAR',
        1043: 'VARCHAR',
        1082: 'DATE',
        1114: 'TIMESTAMP',
        1184: 'TIMESTAMPTZ',
        1700: 'NUMERIC',
        2003: 'DECIMAL',
    }

    mysql_type_code_to_name = {
        0: 'DECIMAL',
        1: 'TINY',
        2: 'SHORT',
        3: 'LONG',
        4: 'FLOAT',
        5: 'DOUBLE',
        6: 'NULL',
        7: 'TIMESTAMP',
        8: 'LONGLONG',
        9: 'INT24',
        10: 'DATE',
        11: 'TIME',
        12: 'DATETIME',
        13: 'YEAR',
        14: 'NEWDATE',
        15: 'VARCHAR',
        16: 'BIT',
        245: 'JSON',
        246: 'NEWDECIMAL',
        247: 'ENUM',
        248: 'SET',
        249: 'TINY_BLOB',
        250: 'MEDIUM_BLOB',
        251: 'LONG_BLOB',
        252: 'BLOB',
        253: 'VAR_STRING',
        254: 'STRING',
        255: 'GEOMETRY'
    }

    sqlite_type_code_to_name = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'BLOB': 'BLOB',
        'REAL': 'REAL',
        'NUMERIC': 'NUMERIC',
    }

    snow_type_code_to_name = {
       
        
    }

    if server_type.upper() == 'POSTGRESQL':
        return postgres_type_code_to_name
    elif server_type.upper() == 'MYSQL':
        return mysql_type_code_to_name
    elif server_type.upper() == 'SQLITE':
        return sqlite_type_code_to_name
    elif server_type.upper() == 'SNOWFLAKE':
        return snow_type_code_to_name
    else:
        type_code_to_name = {}

  


class SearchSheetAndQuerySetList(CreateAPIView):
    serializer_class = serializers.test_data

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_query = serializer.validated_data["search"]
        response_data = []

        try:
            sheet_data_queryset = sheet_data.objects.filter(sheet_name__icontains=search_query)
            queryset_data_queryset = QuerySets.objects.filter(query_name__icontains=search_query)

            for queryset in queryset_data_queryset:
                sheets = sheet_data.objects.filter(queryset_id=queryset.queryset_id)
                sheets_info = [
                    {"sheet_name": sheet.sheet_name, "sheet_id": sheet.id} for sheet in sheets
                ]
                
                response_data.append({
                    "queryset_name": queryset.query_name,
                    "queryset_id": queryset.queryset_id,
                    "sheet_data": sheets_info
                })

            for sheet in sheet_data_queryset:
                if not any(item['queryset_id'] == sheet.queryset_id for item in response_data):
                    queryset = QuerySets.objects.get(queryset_id=sheet.queryset_id)
                    sheets_info = [
                        {"sheet_name": sheet.sheet_name, "sheet_id": sheet.id}
                    ]
                    
                    response_data.append({
                        "queryset_name": queryset.query_name,
                        "queryset_id": queryset.queryset_id,
                        "sheet_data": sheets_info
                    })

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


