from oauth2_provider.models import AccessToken,RefreshToken
import datetime
from pytz import utc
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import *
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from sqlalchemy import create_engine, inspect, MetaData, Table, text,insert
from sqlalchemy.exc import OperationalError
import json,os
from collections import defaultdict
import pandas as pd
from rest_framework import status
import pdfplumber
import plotly.graph_objects as go
from sqlalchemy.orm import sessionmaker
from .serializers import *
from django.db import transaction
from project import settings
from django.urls import reverse
from django.http import JsonResponse
from django.core.serializers import serialize as ss
from io import BytesIO
from rest_framework.decorators import api_view
import re
import sqlite3
import base64
import sys
from quickbooks import models as qb_models, views as qb_views, salesforce_endpoints, salesforce
from django.core.paginator import Paginator
from dashboard.columns_extract import server_connection
from dashboard import roles,previlages,columns_extract,Connections,authentication
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Float, Date, Time, DateTime, Numeric,text,TIMESTAMP
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from django.http.response import HttpResponse
from django.utils.crypto import get_random_string
import os ,io
from django.core.files.uploadedfile import InMemoryUploadedFile
import threading
# from .authentication import signup_thread

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)

def generate_access_from_refresh(refresh_token):
    TOKEN_URL = authentication.TOKEN_URL
    client_id = authentication.CLIENT_ID
    client_secret = authentication.CLIENT_SECRET
    REFRESH_TOKEN = refresh_token

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': client_id,
        'client_secret': client_secret,
        # Add any additional parameters as needed
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code==200:
        data = {
            'status':200,
            'data':response.json()
        }
    else:
        data = {
            'status':response.status_code,
            'data':response
        }
    return data


def tok_user_check(user):
    if UserProfile.objects.filter(id=user,is_active=True).exists():
        # if license_key.objects.filter(user_id=user,key__isnull=True).exists() or license_key.objects.filter(user_id=user,key=None).exists() or license_key.objects.filter(user_id=user,key='').exists():
        #     data = {
        #         "status":404,
        #         "message":"Liscence key not found for this user, please generate liscence key"
        #     }
        # elif license_key.objects.filter(user_id=user,is_validated=False).exists():
        #     data = {
        #         "status":401,
        #         "message":"Please activate the License key to connect"
        #     }
        # elif license_key.objects.filter(user_id=user,expired_at__gte=datetime.datetime.now(utc)):
        #     data = {
        #         "status":401,
        #         "message":"License key expired, please regenerate new license key"
        #     }
        # else:
        usertable=UserProfile.objects.get(id=user)
        user_role = UserRole.objects.filter(user_id=user).values()
        role_id=[rl['role_id'] for rl in user_role]
        data = {
            "status":200,
            "role_id":role_id,
            "user_id":user,
            "usertable":usertable,
            "username":usertable.username,
            "email":usertable.email
        }
    else:
        data = {
            "status":404,
            "message":"User Not Activated, Please activate the account"
        }
    return data


def token_function(token):
    try:
        token1=AccessToken.objects.get(token=token)
    except:
        data = {"message":"Invalid Access Token",
                "status":404}
        return data
    user = token1.user_id
    try:
        rf_token=RefreshToken.objects.get(access_token_id=token1.id,user_id=user)
    except:
        data = {"message":'Session Expired, Please login again',
                    "status":408}
        return data
    # if token1.is_allowed==True:
    #     fn_data=tok_user_check(user)
    #     return fn_data
    if token1.expires < datetime.datetime.now(utc):
        refresh_token=generate_access_from_refresh(rf_token.token)
        if refresh_token['status']==200:
            RefreshToken.objects.filter(id=rf_token.id).delete()
            AccessToken.objects.filter(id=token1.id).delete()
            pass
        else:
            RefreshToken.objects.filter(id=rf_token.id).delete()
            AccessToken.objects.filter(id=token1.id).delete()
            data = {"message":'Session Expired, Please login again',
                    "status":408}
            return data
    else:
        try:
            fn_data=tok_user_check(user)
            return fn_data
        except:
            data = {
                "status":400,
                "message":"Admin not exists/Not assssigned/Role Not created"
            }
            return data      

def test_token(token):
    tok1 = token_function(token)
    return tok1


def encode_string(input_string):
    input_bytes = str(input_string).encode('utf-8')
    encoded_bytes = base64.b64encode(input_bytes)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

def decode_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

    # missing_padding = len(encoded_string) % 4
    # if missing_padding != 0:
    #     encoded_string += '=' * (4 - missing_padding)
    # encoded_bytes = str(encoded_string).encode('utf-8')
    # decoded_bytes = base64.b64decode(encoded_bytes)
    # decoded_string = decoded_bytes.decode('utf-8')
    # return decoded_string

def analyze_document_structure(doc):
    schema_info = {}
    for key, value in doc.items():
        schema_info[key] = type(value).__name__
    return schema_info


def connection_error_messages(dply_name,hostname,username,db_name,port,u_id,database_id,password,server_path,st_id,service_name):
    server_tp=ServerType.objects.get(id=st_id)
    allowed_extensions = ['.db', '.sqlite', '.sqlite3','']
    disallowed_extensions = ['.sh', '.exe', '.bat', '.txt', '.csv', '.xlsx', '.json', '.doc', '.docx', '.ppt', '.pptx', '.pdf', '.xml', '.html', '.htm', '.zip', '.rar', '.tar', '.gz', '.bz2', '.msg', '.ml', '.ipynb', '.py', '.js', '.pl', '.rb', '.php', '.ini', '.cfg', '.yaml', '.yml', '.mdb', '.dbf', '.svg', '.gif', '.png', '.jpg']

    if server_tp.server_type.upper() == 'SQLITE':
        if dply_name == '' or dply_name is None or str(dply_name).strip() == '':
            return Response({'message': "Display name can't be empty"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif ServerDetails.objects.filter(user_id=u_id,display_name=dply_name).exclude(id=database_id).exists():
            return Response({'message':"Display Name Already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif server_path == '' or server_path is None or str(server_path).strip() == '':
            return Response({'message': "Server path can't be empty"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif any(str(server_path).endswith(ext) for ext in disallowed_extensions):
            return Response({'message': f"Invalid file extension. Allowed extensions are: {', '.join(allowed_extensions)}"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not any(str(server_path).endswith(ext) for ext in allowed_extensions):
            return Response({'message': f"Invalid file extension. Allowed extensions are: {', '.join(allowed_extensions)}"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return 200
    else:
        if dply_name=='' or dply_name==None or dply_name ==' ' or dply_name=="":
            return Response({'message':"Display name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif hostname=='' or hostname==None or hostname ==' ' or hostname == "":
            return Response({'message':"Host Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif username=='' or username==None or username ==' ' or username=="":
            return Response({'message':"username Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif port=='' or port==None or port ==' 'or port=="":
            return Response({'message':"Port Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif ServerDetails.objects.filter(user_id=u_id,display_name=dply_name).exclude(id=database_id).exists():
            return Response({'message':"Display Name Already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
        elif password==None or password=='' or password=="" or password==' ': 
            return Response({'message':'empty password field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if port=='1521':
                return 200
            else:
                if server_tp.server_type.upper() == 'ORACLE':
                    if service_name=='' or service_name==None or service_name=="" or service_name==" ":
                        return Response({'message':"Service name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return 200
                else:
                    if db_name=='' or db_name==None or db_name ==' ' or db_name=="":
                        return Response({'message':"Database name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return 200


def database_connection(parameter,engine,dply_name,db_type,hostname,username,encoded_passw,db_name,port,u_id,service_name,server_path,cursor):
    st = ServerType.objects.get(server_type =db_type.upper())
    if port=='':
        port=None
    else:
        port=port
    sd = ServerDetails.objects.create(
            server_type = st.id,
            hostname = hostname,
            username = username,
            password = encoded_passw,
            database = db_name,
            port = port,
            user_id = u_id,
            display_name = dply_name,
            service_name = service_name,
            is_connected=True,
            database_path=server_path
        )
    ServerDetails.objects.filter(id=sd.id).update(created_at=created_at,updated_at=updated_at)
    # cursor.close()
    # engine.dispose()
    return Response(
        {
            "message":"Successfully Connected to DB",
            'display_name':sd.display_name,
            "database":
                {
                    "database_id":sd.id,
                    "database_name":sd.database
                }
            }
        ,status=status.HTTP_200_OK)
    
    
def database_connection_update(dply_name,hostname,username,encoded_passw,db_name,port,u_id,service_name,database_id,server_type_id,server_id,server_path):
        
    sd = ServerDetails.objects.filter(id=server_id).update(
        server_type = server_type_id,
        hostname = hostname,
        username = username,
        password = encoded_passw,
        database = db_name,
        port = port,
        user_id = u_id,
        display_name = dply_name,
        service_name = service_name,
        is_connected=True,
        database_path=server_path,
        updated_at = datetime.datetime.now()
        )
    ServerDetails.objects.filter(id=server_id).update(updated_at=updated_at)
    return Response({'message':"Database Details Updated Successful"},status=status.HTTP_200_OK)
    
class DBConnectionAPI(CreateAPIView):
    
    serializer_class = DataBaseConnectionSerializer
    @csrf_exempt
    @transaction.atomic()
    def post(self, request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_database])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            # db_count=ServerDetails.objects.filter(user_id=tok1['user_id']).count()
            # key=license_key.objects.get(user_id=tok1['user_id'])
            # if db_count<key.max_limit:
            #     pass
            # else:
            #     return Response({'message':'Max_limit of connections are done/connections Not allowed'},status=status.HTTP_406_NOT_ACCEPTABLE)
            serializer=self.serializer_class(data=request.data)
            if serializer.is_valid():
                db_type = serializer.validated_data['database_type']
                hostname = serializer.validated_data['hostname']
                port = serializer.validated_data['port']
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                db_name = serializer.validated_data['database']
                dply_name = serializer.validated_data['display_name']
                service_name = serializer.validated_data['service_name']
                server_path = serializer.validated_data['path']
                try:
                    st = ServerType.objects.get(server_type =db_type.upper())
                except:
                    return Response({'message':'Server_type not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                server_id=None
                conn_status = connection_error_messages(dply_name,hostname,username,db_name,port,tok1['user_id'],server_id,password,server_path,st.id,service_name)
                if conn_status==200:
                    pass
                else:
                    return conn_status
                encoded_passw=encode_string(password)
                if ServerType.objects.filter(server_type =db_type.upper()).exists():
                    ser_data=ServerType.objects.get(server_type=db_type.upper())
                    server_conn=server_connection(username, encoded_passw, db_name, hostname,port,service_name,ser_data.server_type.upper(),server_path)
                    if server_conn['status']==200:
                        engine=server_conn['engine']
                        cursor=server_conn['cursor']
                        parameter=ser_data.server_type.upper()
                        postgres=database_connection(parameter,engine,dply_name,db_type,hostname,username,encoded_passw,db_name,port,tok1['user_id'],service_name,server_path,cursor)
                        return postgres
                    else:
                        # return Response(server_conn['message'],status=server_conn['status'])
                        return Response({'message':server_conn['message']},status=server_conn['status'])
                else:
                    return Response({'message':"Invalid Server/file Type"},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':"Unsupported File Format"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])
    
    @transaction.atomic()
    def put(self, request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_database])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.serializer_class(data=request.data)
            if serializer.is_valid():
                database_id = serializer.validated_data['database_id']
                db_type = serializer.validated_data['database_type']
                hostname = serializer.validated_data['hostname']
                port = serializer.validated_data['port']
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                db_name = serializer.validated_data['database']
                dply_name = serializer.validated_data['display_name']
                service_name = serializer.validated_data['service_name']
                server_path = serializer.validated_data['path']
                try:
                    sd = ServerDetails.objects.get(id=database_id)
                except:
                    return Response({'message':"Invalid Database Id"},status=status.HTTP_404_NOT_FOUND)
                try:
                    st = ServerType.objects.get(server_type =db_type.upper())
                except:
                    return Response({'message':'Server_type not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                conn_status = connection_error_messages(dply_name,hostname,username,db_name,port,tok1['user_id'],sd.id,password,server_path,st.id,service_name)
                if conn_status==200:
                    pass
                else:
                    return conn_status
                encoded_passw=encode_string(password)
                server_conn=server_connection(username, encoded_passw, db_name, hostname,port,service_name,st.server_type.upper(),server_path)
                if server_conn['status']==200:
                    engine=server_conn['engine']
                    cursor=server_conn['cursor']
                    db_conn_up=database_connection_update(dply_name,hostname,username,encoded_passw,db_name,port,tok1['user_id'],service_name,database_id,st.id,sd.id,server_path)
                    cursor.close()
                    # engine.dispose()
                    return db_conn_up
                else:
                    # return Response(server_conn['message'],status=server_conn['status'])
                    return Response({'message':server_conn['message']},status=server_conn['status'])
            else:
                return Response({'message':"Unsupported File Format"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])
        

# class GetTablesOfServerDB(CreateAPIView):
@transaction.atomic()
@api_view(['GET'])
def GetTablesOfServerDB(request,token,database_id):
    if request.method=='GET':
        tok1 = test_token(token)
        if tok1['status']==200:
            if ServerDetails.objects.filter(id=database_id).exists():
                sd = ServerDetails.objects.get(id=database_id)
                st = ServerType.objects.get(id=sd.server_type)
                server_conn=server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
                if server_conn['status']==200:
                    engine=server_conn['engine']
                    cursor=server_conn['cursor']
                else:
                    return Response(server_conn,status=server_conn['status'])
                if st.server_type =='POSTGRESQL' or st.server_type =='MYSQL' or st.server_type=="SQLITE":
                    inspector = inspect(engine)
                    schemas = inspector.get_schema_names()
                    ll= []
                    for i in schemas:
                        if i != 'information_schema':
                            table_names = inspector.get_table_names(schema=i)
                            
                            for table_name in table_names:
                                columns = inspector.get_columns(table_name,schema=i)
                                col = []
                                for column in columns:
                                    col.append({"columns": column['name'].lower(), "datatypes": str(column['type']).lower()})
                                ll.append({"schema":i,"table":table_name,"columns":col})
                        pass
                    cursor.close()
                    # engine.dispose()
                    return Response(
                        {
                            "message":"Successfully Connected to DB",
                            "data":ll,
                            'display_name':sd.display_name,
                            "database":
                                {
                                    "database_id":sd.id,
                                    "database_name":sd.database
                                }
                            }
                        ,status=status.HTTP_200_OK)
                elif st.server_type =='ORACLE':
                    inspector = inspect(engine)
                    table_names = inspector.get_table_names(schema=sd.username)
                    ll=[]    
                    for table_name in table_names:
                        columns = inspector.get_columns(table_name)
                        col = []
                        for column in columns:
                            col.append({"columns": column['name'].lower(), "datatypes": str(column['type']).lower()})
                        ll.append({"schema":sd.username,"table":table_name,"columns":col})
                    cursor.close()
                    # engine.dispose() 
                    return Response(
                        {
                            "message":"Successfully Connected to DB",
                            "data":ll,
                            'display_name':sd.display_name,
                            "database":
                                {
                                    "database_id":sd.id,
                                    "database_name":sd.database
                                }
                            }
                        ,status=status.HTTP_200_OK)
                elif st.server_type=="MONGODB":
                    db=engine
                    final_list={}
                    colms=[]
                    final_ls=[]
                    collections = db.list_collection_names()
                    for collection_name in collections:
                        final_list['schema']=None
                        final_list['table']=collection_name
                        collection = db[collection_name]
                        documents = collection.find()
                        for field in documents:
                            cllist=[]
                            colms.append({'columns':cllist.append(field),'datatypes':None})
                        final_list['columns']=colms
                    final_ls.append(final_list)
                    cursor.close()
                    # engine.dispose()
                    return Response(
                        {
                            "message":"Successfully Connected to DB",
                            "data":final_ls,
                            'display_name':sd.display_name,
                            "database":
                                {
                                    "database_id":sd.id,
                                    "database_name":sd.database
                                }
                            }
                        ,status=status.HTTP_200_OK)
                elif st.server_type.upper()=="MICROSOFTSQLSERVER":
                    tables_query = """
                    SELECT 
                        TABLE_SCHEMA,
                        TABLE_NAME
                    FROM 
                        INFORMATION_SCHEMA.TABLES
                    WHERE 
                        TABLE_TYPE = 'BASE TABLE'
                    """
                    cursor.execute(tables_query)
                    tables = cursor.fetchall()
                    schema_info = {}
                    for table in tables:
                        schema = table.TABLE_SCHEMA
                        table_name = table.TABLE_NAME
                        if schema not in schema_info:
                            schema_info[schema] = {}
                        columns_query = f"""
                        SELECT 
                            COLUMN_NAME,
                            DATA_TYPE
                        FROM 
                            INFORMATION_SCHEMA.COLUMNS
                        WHERE 
                            TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                        ORDER BY 
                            ORDINAL_POSITION
                        """
                        cursor.execute(columns_query)
                        columns = cursor.fetchall()
                        schema_info[schema][table_name] = [(column.COLUMN_NAME, column.DATA_TYPE) for column in columns]
                    formatted_data = []
                    for schema_name, tables in schema_info.items():
                        for table_name, columns in tables.items():
                            table_entry = {"schema": schema_name, "table": table_name, "columns": []}
                            for column_name, data_type in columns:
                                column_entry = {"columns": column_name, "datatypes": data_type}
                                table_entry["columns"].append(column_entry)
                            formatted_data.append(table_entry)
                    cursor.close()
                    # engine.dispose()
                    return Response(
                        {
                            "message":"Successfully Connected to DB",
                            "data":formatted_data,
                            'display_name':sd.display_name,
                            "database":
                                {
                                    "database_id":sd.id,
                                    "database_name":sd.database
                                }
                            }
                        ,status=status.HTTP_200_OK)
                else:
                    return Response({'message':'SERVER not found'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':"Invalid Data Base ID"},status=status.HTTP_404_NOT_FOUND)                           
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
def set_list_elements(new_list):
    global list_elements
    if len(new_list) == 1 and len(new_list[0]) == 2:
        list_elements = new_list
    else:
        raise ValueError("Invalid list format. It should be [['schema_name', 'table_name']]")

        
class GetTableRelationShipAPI(CreateAPIView):
    serializer_class = GetColumnFromTableSerializer
    
    @transaction.atomic()
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                db_id = serializer.validated_data['database_id']
                tables = serializer.validated_data['tables']
                conditions = serializer.validated_data['condition']
                # datatype = serializer.validated_data['datatype']

                
                sd = ServerDetails.objects.get(id=db_id)
                st = ServerType.objects.get(id=sd.server_type)
                server_conn=server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
                if server_conn['status']==200:
                    engine=server_conn['engine']
                    cursor=server_conn['cursor']
                else:
                    return Response({'message':'Invalid credientials'},status=server_conn['status'])
                # Check the connection status
                if conditions == []:
                    try:
                        inspector = inspect(engine)

                        l=[]
                        for schema,table_name in tables:
                            columns = inspector.get_columns(table_name = table_name,schema = schema)
                            col = []
                            for column in columns:
                                col.append({"columns": column['name'].lower(), "datatypes": str(column['type']).lower()})
                            l.append({"table":f'{schema}.{table_name}',"columns":col})
                        
                        if conditions == "" or conditions == []:
                            try:
                                # Iterate through the columns of the Table1 
                                for column1 in l[0]["columns"]:
                                    # Iterate through the columns of the Table2
                                    for column2 in l[1]["columns"]:
                                        # Check if the column names and data types match
                                        if column1["columns"] == column2["columns"] and column1["datatypes"] == column2["datatypes"]:
                                            l.append({'relation':
                                                {
                                                    "datatype":column2['datatypes'],
                                                    "tables":[l[0]['table'],l[1]['table']],
                                                    "condition":["{}.{} = {}.{}".format(l[0]['table'],column1["columns"],l[1]['table'],column2["columns"])]
                                                }
                                            })
                                            return Response(l)
                            except:
                                pass
                            l.append({'relation':
                                {
                                    "datatype":"",
                                    "tables":[l[0]['table'],l[1]['table']],
                                    "condition":[]
                                }
                            })
                            return Response(l)
                        else:
                            l.append({'relation':
                                {
                                    "datatype":"",
                                    "tables":[l[0]['table'],l[1]['table']],
                                    "condition":[condition]
                                }
                            })
                            return Response(l)
                    except Exception as e:
                        return Response({'message':f"Connection error: {e}"})
                else:
                    inspector = inspect(engine)
                    l=[]
                    for schema,table_name in tables:
                        columns = inspector.get_columns(table_name = table_name,schema = schema)
                        col = []
                        for column in columns:
                            col.append({"columns": column['name'].lower(), "datatypes": str(column['type']).lower()})
                        l.append({"table":f'{schema}.{table_name}',"columns":col})
                    
                    # Check if the data types of the condition field match in both tables
                    table1_schema, table1_name = tables[0]
                    table2_schema, table2_name = tables[1]

                    # Extract column names and check their existence
                    for condition in conditions:
                        # Extract column names from the condition
                        table1_column = condition[0].split('=')[0].strip().split('.')[-1]
                        table2_column = condition[0].split('=')[1].strip().split('.')[-1]
                        
                        # Get the list of columns for the specified table
                        column1 = inspector.get_columns(table1_name, schema=table1_schema)

                        # Find the index of the column you're interested in
                        column1_index = next((i for i, col in enumerate(column1) if col['name'] == table1_column), None)
                        
                        column2 = inspector.get_columns(table2_name, schema=table2_schema)

                        # Find the index of the column you're interested in
                        column2_index = next((i for i, col in enumerate(column2) if col['name'] == table2_column), None)

                        if column1_index is not None and column2_index is not None:
                            col1_datatype = column1[column1_index]['type']
                            col2_datatype = column2[column2_index]['type']
                            if str(col1_datatype).split('(')[0].lower() == str(col2_datatype).split('(')[0].lower():
                                pass
                            else:
                                return Response({'message':"Field Datatypes Mismatch {} & {}".format(str(col1_datatype).split('(')[0].lower(),str(col2_datatype).split('(')[0].lower())},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            # Handle the case where one or both columns are not found
                            if column1_index is None:
                                return Response({'message':f"Column '{table1_column}' not found in table '{table1_name}'."},status=status.HTTP_404_NOT_FOUND)
                            if column2_index is None:
                                return Response({'message':f"Column '{table2_column}' not found in table '{table2_name}'."},status=status.HTTP_404_NOT_FOUND)
                        
                    l.append({'relation':
                            {
                                "datatype":str(col1_datatype).split('(')[0],
                                "tables":tables,
                                "condition": conditions
                            }
                        })
                    return Response(l)
            return Response({'message':"Serializer Error"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])
        
            
    @transaction.atomic()
    def put(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                db_id = serializer.validated_data['database_id']
                tables = serializer.validated_data['tables']

                try:
                    set_list_elements(tables)
                except ValueError as e:
                    return Response({"message":f'{e}'},status=status.HTTP_406_NOT_ACCEPTABLE)
                
                try:
                    sd = ServerDetails.objects.get(id=int(db_id))
                except:
                    return Response({'message':"Invalid Database ID"},status=status.HTTP_404_NOT_FOUND)
                
                try:
                    st = ServerType.objects.get(id=sd.server_type)
                except:
                    return Response({'message':"Server Type Not Found"},status=status.HTTP_404_NOT_FOUND)
                
                for schema,table in tables:
                    table_name = f'{schema}.{table}'

                server_conn=server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
                if server_conn['status']==200:
                    engine=server_conn['engine']
                    connection=server_conn['cursor']
                else:
                    return Response(server_conn,status=server_conn['status'])
                if st.server_type.upper()=="POSTGRESQL" or st.server_type =='MYSQL' or st.server_type=="SQLITE":
                    query = text('SELECT * FROM "{}"."{}"'.format(schema,table))
                    inspector = inspect(engine)
                    columns = inspector.get_columns(table,schema=schema)
                elif st.server_type.upper()=="ORACLE":
                    query = text("SELECT * FROM {}".format(table_name))
                    inspector = inspect(engine)
                    columns = inspector.get_columns(table_name)

                result = connection.execute(query)
                col = []
                for column in columns:
                    col.append({"table":table_name,"columns": column['name'].lower(), "datatypes": str(column['type']).lower()})
                rows = result.fetchall()
                data =[]
                for i in rows:
                    a = list(i)
                    data.append(a)
                return Response({"column_data":col,"row_data":data})

            return Response({'message':"Serializer Error"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])

class ListofActiveServerConnections(CreateAPIView):
    
    serializer_class = SearchFilterSerializer
    @transaction.atomic()
    def put(self, request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_database])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                # Search Filter Only works on Display Name Column in Server Details
                search = serializer.validated_data['search']
                page_no = serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                
                if ServerDetails.objects.filter(user_id=tok1['user_id'],is_connected=True).exists() or FileDetails.objects.filter(user_id=tok1['user_id']).exists():
                
                    if search =='':
                        details = ServerDetails.objects.filter(user_id=tok1['user_id'],is_connected=True).values().order_by('-updated_at')
                        filedetai = FileDetails.objects.filter(user_id=tok1['user_id'],quickbooks_user_id=None).values().order_by('-updated_at')
                        quickdetai = qb_models.TokenStoring.objects.filter(user=tok1['user_id']).values().order_by('-updated_at')
                    else:
                        details = ServerDetails.objects.filter(user_id=tok1['user_id'],is_connected=True,display_name__icontains=search).values().order_by('-updated_at')
                        filedetai = FileDetails.objects.filter(user_id=tok1['user_id'],display_name__icontains=search,quickbooks_user_id=None).values().order_by('-updated_at')
                        quickdetai = qb_models.TokenStoring.objects.filter(user=tok1['user_id'],display_name__icontains=search).values().order_by('-updated_at')
                    l =[]
                    for i in details:
                        created_by = "Example" if i['is_sample'] else tok1['username']  # Update created_by based on is_sample
                        st = ServerType.objects.get(id=i['server_type'])
                        data = {
                            "file_id":None,
                            "file_type":None,
                            "database_id":i['id'],
                            "server_type":st.server_type,
                            "is_sample":i['is_sample'],
                            "database_type":st.server_type.lower(),
                            "hostname":i['hostname'],
                            "database":i['database'],
                            "port" :i['port'],
                            "username":i['username'],
                            "service_name":i['service_name'],
                            "display_name":i['display_name'],
                            "is_connected":i['is_connected'],
                            "created_by":created_by,
                            "created_at" : i['created_at'].date(),
                            "updated_at" : i['updated_at'].date()
                        }
                        l.append(data)
                    for q in quickdetai:
                        pr_ids=parent_ids.objects.get(table_id=q['id'])
                        data1 = {
                            "file_id":None,
                            "file_type":None,
                            "database_id":pr_ids.id,
                            "server_type":str(q['parameter']).upper(),
                            "database_type":str(q['parameter']).lower(),
                            "hostname":None,
                            "database":None,
                            "port" :None,
                            "username":None,
                            "service_name":None,
                            "display_name":q['display_name'],
                            "is_connected":None,
                            "created_by":tok1['username'],
                            "created_at" : q['created_at'].date(),
                            "updated_at" : q['updated_at'].date()
                        }
                        l.append(data1)
                    for h in filedetai:
                        st = FileType.objects.get(id=h['file_type'])
                        data1 = {
                            "file_id":h['id'],
                            "file_type":st.file_type,
                            "database_id":None,
                            "server_type":st.file_type,
                            "database_type":st.file_type.lower(),
                            "hostname":None,
                            "database":None,
                            "port" :None,
                            "username":None,
                            "service_name":None,
                            "display_name":h['display_name'],
                            "is_connected":None,
                            "created_by":tok1['username'],
                            "created_at" : h['uploaded_at'].date(),
                            "updated_at" : h['updated_at'].date()
                        }
                        l.append(data1)
                    try:
                        paginator = Paginator(l,page_count)
                        page = request.GET.get("page",page_no)
                        object_list = paginator.page(page)
                        re_data = list(object_list)
                        data1 = {
                            "status":200,
                            "sheets":re_data,
                            "total_pages":paginator.num_pages,
                            "items_per_page":page_count,
                            "total_items":paginator.count
                        }
                        return Response(data1,status=status.HTTP_200_OK)
                    except:
                        return Response({'message':'Empty page, data not exists'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'connection':[]},status=status.HTTP_200_OK)
            else:
                return Response({'message':"Serialzer Error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])


def default_query_name(queryset_id,query_name):
    en_str=encode_string(str(queryset_id))
    if query_name==[] or query_name=='' or query_name=="":
        query_name=str('untitled_')+str(en_str)
    else:
        query_name=query_name
    return query_name
    


def custom_query_data(row_limit,paramet,server_id,custom_query,u_id,datasorce_queryset_id,server_type,query_name,parameter,queryset_id):
    if paramet=="server":
        server_id1=server_id
        file_id=None
        try:
            sd = ServerDetails.objects.get(id=server_id1)
        except:
            return Response({'message':"Invalid Database ID"},status=status.HTTP_404_NOT_FOUND)
        try:
            st = ServerType.objects.get(id=sd.server_type)
        except Exception as e:
            return Response({'message':"Server Type Not Found"},status=status.HTTP_404_NOT_FOUND)
        
        server_conn=server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
        if server_conn['status']==200:
            engine=server_conn['engine']
            connection=server_conn['cursor']
        else:
            return Response(server_conn,status=server_conn['status'])
    else:
        server_id1=None
        file_id=server_id
        file_type=server_type
        try:
            filedata = FileDetails.objects.get(user_id=u_id,id=file_id)
        except:
            return Response({'message':"Invalid file ID"},status=status.HTTP_404_NOT_FOUND)
        files_data=columns_extract.file_details(file_type,filedata)
        if files_data['status']==200:
            engine=files_data['engine']
            connection=files_data['cursor']
            tables=files_data['tables_names']
        else:
            return Response({'message':files_data['message']},status=files_data['status'])

    start_time=datetime.datetime.now(utc)
    # Execute a query
    try: 
        if server_type=="MICROSOFTSQLSERVER":
            clean_query_string = re.sub('[;\[\]]', '', custom_query)
            query1 = text(clean_query_string)
            if 'limit' in str(query1).lower():
                query=query1
            else:
                query = "{} limit {}".format(query1,row_limit)
            result = connection.execute(query)
            columns_info = connection.description
            column_list = [column[0] for column in columns_info]
            data_type_list = [data_type[1].__name__ for data_type in columns_info]
            rows = result.fetchall()

            query12 = "{}".format(query1)
            result12 = connection.execute(query12)
            columns_info12 = connection.description
            column_list12 = [column[0] for column in columns_info12]
            data_type_list12 = [data_type[1].__name__ for data_type in columns_info12]
            rows12 = result12.fetchall()
        else:
            clean_query_string = re.sub(';', '', custom_query)
            if 'limit' in str(clean_query_string).lower():
                query11=clean_query_string
            else:
                query11 = "{} limit {}".format(clean_query_string,row_limit)
            query = text(query11)
            result = connection.execute(query)
            column_names = result.keys()
            column_list = [column for column in column_names]
            rows = result.fetchall()

            query12 = text(clean_query_string)
            result12 = connection.execute(query12)
            column_names12 = result12.keys()
            column_list12 = [column for column in column_names12]
            rows12 = result12.fetchall()
    except Exception as e:
        return Response({'message':f'{str(e)}'},status=status.HTTP_400_BAD_REQUEST)
    
    column_counts = {}  #### ambigious error for repeated column names in query.
    colum_ambi_list=[]
    for column in column_list:
        if column in column_counts:
            column_counts[column] += 1
        else:
            column_counts[column] = 1
    repeated_columns = {column: count for column, count in column_counts.items() if count > 1}
    for column, count in repeated_columns.items():
        colum_ambi_list.append(column)
        # print(f"{column}: {count} times")
    if colum_ambi_list==[]:
        pass
    else:
        return Response({'message':'column reference {} is ambiguous'.format(colum_ambi_list[0])},status=status.HTTP_406_NOT_ACCEPTABLE)
 
    data =[]
    for i in rows:
        a = list(i)
        data.append(a)
    
    row_count=[]
    for m in rows12:
        a12 = list(m)
        row_count.append(a12)

    ## Give the auto name if name not given
    # if query_name==[] or query_name=='' or query_name=="":
    #     pattern = r"^.{0,20}"
    #     match = re.search(pattern, str(custom_query))
    #     m1=str(match.group()).replace('*','').replace(' ','')
    #     query_name=m1
    # else:
    #     query_name=query_name
        
    if parameter=="SAVE":
        if queryset_id=='' or queryset_id==None:
            qs=QuerySets.objects.create(
                user_id = u_id,
                server_id = server_id1,
                file_id=file_id,
                is_custom_sql = True,
                custom_query = clean_query_string,
                query_name=query_name,
                created_at=created_at,
                updated_at=updated_at
            )
            qs.save()
            updated_qr_name=default_query_name(qs.queryset_id,query_name)
            QuerySets.objects.filter(queryset_id=qs.queryset_id).update(created_at=created_at,updated_at=updated_at,query_name=updated_qr_name)
        else:
            updated_qr_name=default_query_name(queryset_id,query_name)
            QuerySets.objects.filter(queryset_id=queryset_id).update(
                    custom_query = clean_query_string,query_name=updated_qr_name,updated_at=updated_at,
                    file_id=file_id,user_id=u_id)
            QuerySets.objects.filter(queryset_id=queryset_id).update(updated_at=updated_at)
            qs = QuerySets.objects.get(queryset_id=queryset_id)
    elif parameter=="UPDATE":
        if queryset_id=='' or queryset_id==None:
            return Response({'message':'Empty queryset_id field is not accepted'},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            updated_qr_name=default_query_name(queryset_id,query_name)
            if file_id==None:
                QuerySets.objects.filter(queryset_id=queryset_id,server_id=server_id1,user_id=u_id).update(
                    custom_query = clean_query_string,query_name=updated_qr_name,updated_at=updated_at)
            else:
                QuerySets.objects.filter(queryset_id=queryset_id,file_id=file_id,user_id=u_id).update(
                    custom_query = clean_query_string,query_name=updated_qr_name,updated_at=updated_at)
            QuerySets.objects.filter(queryset_id=queryset_id).update(updated_at=updated_at)
            qs = QuerySets.objects.get(queryset_id=queryset_id)
    elif parameter=="GET":
        qs = QuerySets.objects.get(queryset_id=queryset_id)

    end_time=datetime.datetime.now(utc)
    data={
        "database_id":server_id1,
        "file_id":file_id,
        "query_name":qs.query_name,
        "datasorce_queryset_id":datasorce_queryset_id,
        "query_set_id" : qs.queryset_id, 
        "custom_query" : qs.custom_query,
        "column_data" : column_list,
        'row_data' : data,
        "is_custom_query":qs.is_custom_sql,
        "query_exection_time":end_time-start_time,
        "total_rows":len(row_count),
        "no_of_rows":len(data),
        "no_of_columns":len(column_list),
        "created_at":qs.created_at,
        "updated_at":qs.updated_at,
        "query_exection_st":start_time.time(),
        "query_exection_et":end_time.time()
        }
    if paramet!="server":
        columns_extract.delete_tables_sqlite(connection,engine,files_data['tables_names'])
    else:
        pass
    connection.close()
    # engine.dispose()
    return Response(data,status=status.HTTP_200_OK)



def custom_query_main(serializer,user_id,para,server_p,file_p,custom_query_tb):
    custom_query = serializer.validated_data['custom_query']
    server_id = serializer.validated_data['database_id']
    query_name = serializer.validated_data['query_name']
    queryset_id = serializer.validated_data['queryset_id']
    file_id = serializer.validated_data['file_id']
    row_limit = serializer.validated_data['row_limit']
    if para=="UPDATE" or para=="SAVE":
        custom_query=custom_query
    elif para=="GET":
        custom_query=custom_query_tb
    if queryset_id==None or queryset_id=='' or queryset_id=="":
        datasorce_queryset_id=None
    else:
        if DataSource_querysets.objects.filter(queryset_id=queryset_id).exists():
            quer_tb=DataSource_querysets.objects.get(queryset_id=queryset_id,server_id=server_id,user_id=user_id)
            datasorce_queryset_id=quer_tb.datasource_querysetid
        else:
            datasorce_queryset_id=None
    if file_id==None or file_id=='':
        us_data={
            'user_id':user_id
        }
        try:
            salesforce_Data=salesforce_endpoints.salesforce_query_data(server_id,us_data,custom_query)
            return salesforce_Data
        except:
            pass
        if ServerDetails.objects.filter(id=server_id).exists():
            srtb=ServerDetails.objects.get(id=server_id)
            srtyp=ServerType.objects.get(id=srtb.server_type)
        else:
            return Response({'message':'Server id not exists'},status=status.HTTP_404_NOT_FOUND)
        final_data=custom_query_data(row_limit,server_p,server_id,custom_query,user_id,datasorce_queryset_id,srtyp.server_type.upper(),query_name,para,queryset_id=queryset_id)
        return final_data
    else:
        if FileDetails.objects.filter(id=file_id).exists():
            file_db_data=FileDetails.objects.get(id=file_id)
            file_data=FileType.objects.get(id=file_db_data.file_type)
        else:
            return Response({'message':'file_details_id/file_type not exists'},status=status.HTTP_404_NOT_FOUND)
        final_data=custom_query_data(row_limit,file_p,file_db_data.id,custom_query,user_id,datasorce_queryset_id,file_data.file_type.upper(),query_name,para,queryset_id=queryset_id)
        return final_data


class CustomSQLQuery(CreateAPIView):
    serializer_class = CustomSQLSerializer
    
    # @transaction.atomic()
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_custom_sql,previlages.view_custom_sql])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                query_name = serializer.validated_data['query_name']
                queryset_id = serializer.validated_data['queryset_id']
                para="SAVE"
                file_p="file"
                server_p="server"
                custom_query_tb=None
                if queryset_id=='' or queryset_id==None:
                    if query_name==None or query_name=='':
                        pass
                    else:
                        if QuerySets.objects.filter(query_name=query_name,user_id=tok1['user_id']).exists():
                            return Response({'message':'queryset name alredy exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    qrtb=QuerySets.objects.get(queryset_id=queryset_id)
                    qr_name=qrtb.query_name
                    if str(qr_name)==str(query_name) or query_name==None or query_name=='':
                        pass
                    else:
                        if QuerySets.objects.filter(user_id=tok1['user_id'],query_name=query_name).exists(): ##queryset_id=queryset_id,
                            return Response({'message':'queryset name alredy exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                cust_query=custom_query_main(serializer,tok1['user_id'],para,server_p,file_p,custom_query_tb)
                return cust_query
            else:
                return Response({"message":"Serializer Error"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

    # @transaction.atomic()
    def put(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_custom_sql,previlages.view_custom_sql])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                query_name = serializer.validated_data['query_name']
                queryset_id = serializer.validated_data['queryset_id']
                para="UPDATE"
                file_p="file"
                server_p="server"
                custom_query_tb=None
                if queryset_id=='' or queryset_id==None:
                    if QuerySets.objects.filter(query_name=query_name,user_id=tok1['user_id']).exists():
                        return Response({'message':'queryset name alredy exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    qrtb=QuerySets.objects.get(queryset_id=queryset_id)
                    qr_name=qrtb.query_name
                    if str(qr_name)==str(query_name):
                        pass
                    else:
                        if QuerySets.objects.filter(user_id=tok1['user_id'],query_name=query_name).exists(): #,queryset_id=queryset_id
                            return Response({'message':'queryset name alredy exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                cust_query=custom_query_main(serializer,tok1['user_id'],para,server_p,file_p,custom_query_tb)
                return cust_query
            else:
                return Response({"message":"Serializer Error"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

class custom_query_get(CreateAPIView):
    serializer_class=CustomSQLSerializer

    # @transaction.atomic()
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_custom_sql])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                queryset_id = serializer.validated_data['queryset_id']
                para="GET"
                file_p="file"
                server_p="server"
                if queryset_id=='' or queryset_id==None:
                    return Response({'message':'Empty queryset_id field is not accepted'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    try:
                        qrset=QuerySets.objects.get(user_id=tok1['user_id'],queryset_id=queryset_id)
                    except:
                        return Response({'message','Data not exists'},status=status.HTTP_404_NOT_FOUND)
                cust_query=custom_query_main(serializer,tok1['user_id'],para,server_p,file_p,qrset.custom_query)
                return cust_query
            else:
                return Response({"message":"Serializer Error"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])


@api_view(['DELETE'])
def query_delete(request,query_set_id,token):
    if request.method=='DELETE':
        role_list=roles.get_previlage_id(previlage=[previlages.delete_custom_sql])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if QuerySets.objects.filter(user_id=tok1['user_id'],queryset_id=query_set_id).exists():
                qrdt=QuerySets.objects.get(user_id=tok1['user_id'],queryset_id=query_set_id)
            else:
                return Response({'message':'query_set_id not exists for this user'},status=status.HTTP_404_NOT_FOUND)
            
            if qrdt.is_sample == True:
                return Response({'message':"Sample Dashboard Queryset cannot be deleted"},status=status.HTTP_403_FORBIDDEN)

            Connections.delete_data(query_set_id,qrdt.server_id,tok1['user_id'])
            return Response({'message':'Deleted successfully'},status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class query_Name_save(CreateAPIView):
    serializer_class=query_save_serializer

    @transaction.atomic
    def put(self,request,token):
        # role_list=roles.get_previlage_id(previlage=[previlages.edit_custom_sql,previlages.create_custom_sql,previlages.view_custom_sql])
        # tok1 = roles.role_status(token,role_list)
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                database_id = serializer.validated_data['database_id']
                query_set_id= serializer.validated_data['query_set_id']
                query_name= serializer.validated_data['query_name']
                # custom_query= serializer.validated_data['custom_query']
                file_id= serializer.validated_data['file_id']
                # clean_query_string = re.sub(';', '', custom_query)
                if file_id==None or file_id=='':
                    if ServerDetails.objects.filter(id=database_id,user_id=tok1['user_id']).exists():
                        pass
                    else:
                        return Response({'message':'server id not exists'},status=status.HTTP_404_NOT_FOUND)
                    if QuerySets.objects.filter(user_id=tok1['user_id'],server_id=database_id,queryset_id=query_set_id).exists():
                        qr_name=QuerySets.objects.get(user_id=tok1['user_id'],server_id=database_id,queryset_id=query_set_id)
                        if qr_name.query_name==query_name:
                            pass
                        else:
                            if QuerySets.objects.filter(user_id=tok1['user_id'],server_id=database_id,query_name=query_name).exists():
                                return Response({'message':'Query name already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                pass
                        QuerySets.objects.filter(user_id=tok1['user_id'],server_id=database_id,queryset_id=query_set_id).update(query_name=query_name,
                                                                                                                                updated_at=datetime.datetime.now())
                        return Response({'message':'Query saved successfylly'},status=status.HTTP_200_OK)
                    else:
                        return Response({'message':'Details not found'},status=status.HTTP_404_NOT_FOUND)
                else:
                    if FileDetails.objects.filter(id=file_id).exists():
                        pass
                    else:
                        return Response({'message':'File id not exists'},status=status.HTTP_404_NOT_FOUND)
                    if QuerySets.objects.filter(user_id=tok1['user_id'],file_id=file_id,queryset_id=query_set_id).exists():
                        qr_name=QuerySets.objects.get(user_id=tok1['user_id'],file_id=file_id,queryset_id=query_set_id)
                        if qr_name.query_name==query_name:
                            pass
                        else:
                            if QuerySets.objects.filter(user_id=tok1['user_id'],file_id=file_id,query_name=query_name).exists():
                                return Response({'message':'Query name already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                pass
                        QuerySets.objects.filter(user_id=tok1['user_id'],file_id=file_id,queryset_id=query_set_id).update(query_name=query_name,
                                                                                                                                updated_at=datetime.datetime.now())
                        return Response({'message':'Query saved successfylly'},status=status.HTTP_200_OK)
                    else:
                        return Response({'message':'Details not found'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        
    
@api_view(['DELETE'])
@transaction.atomic
def DBDisconnectAPI(request,token,database_id):
    if request.method=='DELETE':
        role_list=roles.get_previlage_id(previlage=[previlages.delete_database])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if ServerDetails.objects.filter(id=database_id).exists():
                sdt=ServerDetails.objects.get(id=database_id)
                if sdt.is_sample == True:
                    return Response({'message':"Cannot Deleted Default Database"},status=status.HTTP_403_FORBIDDEN)
                qr_list=QuerySets.objects.filter(server_id=sdt.id).values()
                for qr_id in qr_list:
                    query_set_id=qr_id['queryset_id']
                    Connections.delete_data(query_set_id,sdt.id,tok1['user_id'])
                ServerDetails.objects.get(id=database_id).delete()
                return Response({'message':'Database Deleted Successful'},status=status.HTTP_200_OK)
            else:
                try:
                    pr_id=parent_ids.objects.get(id=database_id)
                    qb_id_1=columns_extract.parent_child_ids(pr_id.id,parameter=pr_id.parameter)
                    if pr_id.parameter=='salesforce':
                        qb_models.TokenStoring.objects.filter(salesuserid=qb_id_1).delete()
                    elif pr_id.parameter=='quickbooks':
                        qb_models.TokenStoring.objects.filter(qbuserid=qb_id_1).delete()
                    return Response({'message':'Database Deleted Successful'},status=status.HTTP_200_OK)
                except:
                    return Response({"message":"Invalid Database ID"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method Not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)

class GetServerTablesList(CreateAPIView):
    serializer_class = SearchFilterSerializer
    
    @csrf_exempt
    def post(self, request,token,database_id):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            
            # Search Filter Only works on Display Name Column in Server Details
            search_table_name = serializer.validated_data['search']
            querySetId = serializer.validated_data['querySetId']
            tok1 = test_token(token)
            if tok1['status'] == 200:
                if querySetId==None or querySetId=='':
                    queryset_name=None
                else:
                    if QuerySets.objects.filter(queryset_id=querySetId,user_id=tok1['user_id']).exists():
                        qrtb=QuerySets.objects.get(queryset_id=querySetId)
                        queryset_name=qrtb.query_name
                    else:
                        return Response({'message':'queryset not exists'},status=status.HTTP_404_NOT_FOUND)
                try:
                    pr_id=parent_ids.objects.get(id=database_id)
                    qb_id_1=columns_extract.parent_child_ids(pr_id.id,parameter=pr_id.parameter)
                    if pr_id.parameter=="quickbooks":
                        quicboooks_tb=qb_models.TokenStoring.objects.get(qbuserid=qb_id_1)
                        table_qb=[]
                        filtered_urls = [url for url in qb_views.qb_urls if search_table_name in url.lower()] # search for thr tables
                        if filtered_urls==[] or filtered_urls =='':
                            qb_table_names=qb_views.qb_urls
                        else:
                            qb_table_names=filtered_urls
                        for i2 in qb_table_names:
                            table_qb.append({"schema":quicboooks_tb.display_name,"table":i2,"columns":[]})
                        schemaqb = [{"schema":quicboooks_tb.display_name,"tables":table_qb}]  ##{"schema":quicboooks_tb.display_name,"tables":[]},
                        return Response(
                                {
                                    "message": "Successfully Connected to quickbooks",
                                    "queryset_name":queryset_name,
                                    "data": {"schemas":schemaqb},
                                    'display_name': quicboooks_tb.display_name,
                                }, status=status.HTTP_200_OK)
                    elif pr_id.parameter=="salesforce":
                        table_qb=[]
                        quicboooks_tb=qb_models.TokenStoring.objects.get(salesuserid=qb_id_1)
                        # table_qb=salesforce_endpoints.table_columns(database_id,tok1,quicboooks_tb.display_name,queryset_name,search_table_name)## ADD search for salesforce columns
                        # return table_qb
                        filtered_urls = [url for url in salesforce.salesforce_tables if search_table_name in url.lower()] # search for thr tables
                        if filtered_urls==[] or filtered_urls =='':
                            qb_table_names=salesforce.salesforce_tables
                        else:
                            qb_table_names=filtered_urls
                        for i2 in qb_table_names:
                            table_qb.append({"schema":quicboooks_tb.display_name,"table":i2,"columns":[]})
                        schemaqb = [{"schema":quicboooks_tb.display_name,"tables":table_qb}]  ##{"schema":quicboooks_tb.display_name,"tables":[]},
                        return Response(
                                {
                                    "message": "Successfully Connected to salesforce",
                                    "queryset_name":queryset_name,
                                    "data": {"schemas":schemaqb},
                                    'display_name': quicboooks_tb.display_name,
                                }, status=status.HTTP_200_OK)
                except:
                    pass
                if ServerDetails.objects.filter(id=database_id).exists():
                    sd = ServerDetails.objects.get(id=database_id)
                    st = ServerType.objects.get(id=sd.server_type)
                    server_conn=server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
                    if server_conn['status']==200:
                        engine=server_conn['engine']
                        cursor=server_conn['cursor']
                    else:
                        return Response(server_conn,status=server_conn['status'])

                    if st.server_type.upper()=="POSTGRESQL" or st.server_type =='MYSQL' or st.server_type=="SQLITE":
                        inspector = inspect(engine)
                        schemas = inspector.get_schema_names()
                        result = {"schemas": []}
                        for i in schemas:
                            if i != 'information_schema':
                                ll = []
                                table_names = inspector.get_table_names(schema=i)
                                table_names_sorted = sorted(table_names)
                                if search_table_name == '' or search_table_name == ' ' or search_table_name == None :
                                    for table_name in table_names_sorted:
                                        columns = inspector.get_columns(table_name, schema=i)
                                        cols = [{"column": column['name'], "datatype": str(column['type']).lower()} for column in columns] #.lower()
                                        ll.append({"schema":i,"table":table_name,"columns":cols})
                                else:
                                    filter_table_names = [table_name for table_name in table_names_sorted if '{}'.format(search_table_name) in table_name.lower()]
                                    for table in filter_table_names:
                                        columns = inspector.get_columns(table, schema=i)
                                        cols = [{"column": column['name'], "datatype": str(column['type']).lower()} for column in columns] #.lower()
                                        ll.append({"schema":i,"table":table,"columns":cols})
                                if ll ==[] :
                                    pass
                                else:
                                    result["schemas"].append({"schema": i, "tables": ll})
                        cursor.close()
                        # engine.dispose()
                        return Response(
                            {
                                "message": "Successfully Connected to DB",
                                "queryset_name":queryset_name,
                                "data": result,
                                'display_name': sd.display_name,
                                "database": {
                                    "database_id": sd.id,
                                    "server_type": st.server_type,
                                    "hostname": sd.hostname,
                                    "database": sd.database,
                                    "port": sd.port,
                                    "username": sd.username,
                                    "service_name": sd.service_name,
                                    "display_name": sd.display_name,
                                }
                            }, status=status.HTTP_200_OK)
                    elif st.server_type.upper()=="ORACLE":
                        # Combine tables and columns query into a single efficient query using JOIN
                        combined_query = """
                            SELECT u.USERNAME AS schema_name, t.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE
                            FROM ALL_USERS u
                            LEFT JOIN ALL_TABLES t ON u.USERNAME = t.OWNER
                            LEFT JOIN ALL_TAB_COLUMNS c ON t.OWNER = c.OWNER AND t.TABLE_NAME = c.TABLE_NAME
                            ORDER BY u.USERNAME, t.TABLE_NAME, c.COLUMN_ID
                        """
                        # Fetch all data in one query execution
                        result = cursor.execute(text(combined_query)).fetchall()
                        # Organize data into a schema-table-columns structure
                        data_structure = {"schemas": []}
                        schema_dict = {}
                        # Process the result set
                        for row in result:
                            schema = row[0]
                            table = row[1]
                            column = row[2]
                            data_type = row[3]
                            if search_table_name==None or search_table_name=='' or search_table_name=="":
                                pass
                            else:
                                try:
                                    if search_table_name and search_table_name not in column:
                                        continue
                                except:
                                    pass
                            if schema not in schema_dict:
                                schema_dict[schema] = {}
                            if table:
                                if table not in schema_dict[schema]:
                                    schema_dict[schema][table] = {"schema": schema, "table": table, "columns": []}
                                if column:
                                    schema_dict[schema][table]["columns"].append({"column": column, "datatype": data_type})
                        for schema_name in sorted(schema_dict.keys()):
                            tables = [table for table in schema_dict[schema_name].values()]
                            data_structure["schemas"].append({"schema": schema_name, "tables": tables})
                        filtered_schemas = []
                        for schema in data_structure['schemas']:
                            # Filter tables where columns are not empty
                            filtered_tables = [table for table in schema['tables'] if table['columns']]
                            # Only add schema if it has non-empty tables
                            if filtered_tables:
                                filtered_schemas.append({
                                    "schema": schema['schema'],
                                    "tables": filtered_tables
                                })
                        cleaned_data_dict = {'schemas': filtered_schemas}
                        cursor.close()
                        # # engine.dispose()
                        return Response(
                            {
                                "message": "Successfully Connected to DB",
                                "queryset_name":queryset_name,
                                "data": cleaned_data_dict,
                                'display_name': sd.display_name,
                                "database": {
                                    "database_id":sd.id,
                                    "server_type":st.server_type,
                                    "hostname":sd.hostname,
                                    "database":sd.database,
                                    "port" :sd.port,
                                    "username":sd.username,
                                    "service_name":sd.service_name,
                                    "display_name":sd.display_name,
                                }
                            }, status=status.HTTP_200_OK)
                    elif st.server_type.upper()=="MONGODB":
                        db=engine
                        final_list={}
                        colms=[]
                        final_ls=[]
                        collections = db.list_collection_names()
                        for collection_name in collections:
                            final_list['schema']=None
                            final_list['table']=collection_name
                            collection = db[collection_name]
                            documents = collection.find()
                            for field in documents:
                                cllist=[]
                                colms.append({'columns':cllist.append(field),'datatypes':None})
                            final_list['columns']=colms
                        final_ls.append(final_list)
                        result = {"schemas": [{"schema": None, "tables": final_ls}]}
                        # cursor.close()
                        # engine.dispose()
                        return Response(
                            {
                                "message": "Successfully Connected to DB",
                                "queryset_name":queryset_name,
                                "data": result,
                                'display_name': sd.display_name,
                                "database": {
                                    "database_id":sd.id,
                                    "server_type":st.server_type,
                                    "hostname":sd.hostname,
                                    "database":sd.database,
                                    "port" :sd.port,
                                    "username":sd.username,
                                    "service_name":sd.service_name,
                                    "display_name":sd.display_name,
                                }
                            }, status=status.HTTP_200_OK)
                    elif st.server_type.upper()=="MICROSOFTSQLSERVER":
                        tables_query = """
                        SELECT 
                            TABLE_SCHEMA,
                            TABLE_NAME
                        FROM 
                            INFORMATION_SCHEMA.TABLES
                        WHERE 
                            TABLE_TYPE = 'BASE TABLE'
                        ORDER BY 
                            TABLE_SCHEMA, TABLE_NAME
                        """
                        cursor.execute(tables_query)
                        tables = cursor.fetchall()
                        schema_info = {}
                        for table in tables:
                            schema = table.TABLE_SCHEMA
                            table_name = table.TABLE_NAME
                            if schema not in schema_info:
                                schema_info[schema] = {}
                            columns_query = f"""
                            SELECT 
                                COLUMN_NAME,
                                DATA_TYPE
                            FROM 
                                INFORMATION_SCHEMA.COLUMNS
                            WHERE 
                                TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                            ORDER BY 
                                ORDINAL_POSITION
                            """
                            cursor.execute(columns_query)
                            columns = cursor.fetchall()
                            schema_info[schema][table_name] = [(column.COLUMN_NAME, column.DATA_TYPE) for column in columns]

                        formatted_data = []
                        for schema_name, tables in schema_info.items():
                            schema_entry = {"schema": schema_name, "tables": []} 
                            for table_name, columns in tables.items():
                                # If search_field is None or empty, include all tables
                                if search_table_name is None or search_table_name == "" or search_table_name in table_name:
                                    table_entry = {"schema": schema_name, "table": table_name, "columns": []}
                                    for column_name, data_type in columns:
                                        column_entry = {"column": column_name, "datatype": data_type}
                                        table_entry["columns"].append(column_entry)
                                    schema_entry["tables"].append(table_entry)
                            # Only add the schema entry if it contains tables
                            if schema_entry["tables"]:
                                formatted_data.append(schema_entry)
                        result12 = {"schemas": formatted_data}

                        # formatted_data = []
                        # for schema_name, tables in schema_info.items():
                        #     schema_entry = {"schema": schema_name, "tables": []} 
                        #     for table_name, columns in tables.items():
                        #         table_entry = {"schema": schema_name, "table": table_name, "columns": []}
                        #         for column_name, data_type in columns:
                        #             column_entry = {"column": column_name, "datatype": data_type}
                        #             table_entry["columns"].append(column_entry)
                        #         schema_entry["tables"].append(table_entry)
                        #     formatted_data.append(schema_entry)
                        # result12 = {"schemas":formatted_data}
    
                        cursor.close()
                        # engine.dispose()
                        return Response(
                            {
                                "message":"Successfully Connected to DB",
                                "queryset_name":queryset_name,
                                "data":result12,
                                'display_name':sd.display_name,
                                "database":
                                    {
                                        "database_id":sd.id,
                                        "database_name":sd.database
                                    }
                                }
                            ,status=status.HTTP_200_OK)
                    elif st.server_type.upper()=="SNOWFLAKE":
                        inspector = inspect(engine)
                        schemas = inspector.get_schema_names()
                        schema_info = []
                        for schema in schemas:
                            tables = inspector.get_table_names(schema=schema)
                            tables_info = []
                            table_names_sorted = sorted(tables)
                            for table in table_names_sorted:
                                columns = inspector.get_columns(table, schema=schema)
                                columns_info = [{'column': col['name'], 'datatype': str(col['type'])} for col in columns]
                                tables_info.append({
                                    "schema": schema,
                                    "table": table,
                                    "columns": columns_info
                                })
                            schema_info.append({
                                "schema": schema,
                                "tables": tables_info
                            })
                        cursor.close()
                        # engine.dispose()
                        return Response(
                            {
                                "message":"Successfully Connected to DB",
                                "queryset_name":queryset_name,
                                "data":{'schemas':schema_info},
                                'display_name':sd.display_name,
                                "database":
                                    {
                                        "database_id":sd.id,
                                        "database_name":sd.database
                                    }
                                }
                            ,status=status.HTTP_200_OK)
                    else:
                        return Response({'message':"server not exists"},status=status.HTTP_404_NOT_FOUND)  
                else:
                    return Response({'message':"Invalid Data Base ID"},status=status.HTTP_404_NOT_FOUND)                           
            else:
                return Response(tok1,status=tok1['status'])


def reassign_user_sample_dashboard(user):
    usertable=UserProfile.objects.get(id=user)
    time_since_creation = timezone.now() - usertable.created_at
    
    # Check if the account is active for 2 days (48 hours)
    if time_since_creation >= timedelta(days=2) and usertable.demo_account == True:
        
        server = ServerDetails.objects.get(user_id = usertable.id)
        QuerySets.objects.filter(user_id = usertable.id).delete()
        ChartFilters.objects.filter(user_id = usertable.id).delete()
        SheetFilter_querysets.objects.filter(user_id = usertable.id).delete()
        DataSource_querysets.objects.filter(user_id = usertable.id).delete()
        DataSourceFilter.objects.filter(user_id = usertable.id).delete()
        sheet_data.objects.filter(user_id = usertable.id).delete()
        dashboard_data.objects.filter(user_id = usertable.id).delete()
        DashboardFilters.objects.filter(user_id = usertable.id).delete()
        UserProfile.objects.filter(id = usertable.id).update(demo_account = False)
        
        # Call the import_data command with the user_id
        try:
            call_command('sample_dashboard', usertable.id, server.id)
            call_command('sample_dashboard3', usertable.id, server.id)
            call_command('sample_dashboard4', usertable.id, server.id)
            call_command('sample_dashboard5', usertable.id, server.id)
        except Exception as e:
            return Response({"message":str(e)},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        pass
    
def new_dashboard_reassign(request):
    usertable=UserProfile.objects.all().order_by('id')   #filter(id=4).order_by('id')
    user_ids = list(usertable.values_list('id', flat=True))
    
    for i in user_ids:
        try:
            server = ServerDetails.objects.get(user_id = i,is_sample=True)
            print(server,i)
        except:
            BASE_DIR = settings.BASE_DIR
            # Construct the full path to the file
            file_path = os.path.join(BASE_DIR, 'insightapps-sample')
            
            # Load the file content
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Create an InMemoryUploadedFile instance
            file_obj = InMemoryUploadedFile(
                file=io.BytesIO(file_content),  # File content wrapped in BytesIO
                field_name='database_path',
                name='insightapps-sample',
                content_type='application/x-sqlite3',
                size=len(file_content),
                charset=None
            )
            
            server =ServerDetails.objects.create(
                server_type = 4,
                user_id = i,
                is_sample = True,
                database_path = file_obj,
                display_name = 'Example',
                is_connected = True,
                created_at = datetime.datetime.now(),
                updated_at = datetime.datetime.now()
            )
            print(server, i)
            server.save()

        QuerySets.objects.filter(user_id = i,is_sample=True).delete()
        sheet_data.objects.filter(user_id = i,is_sample=True).delete()
        dashboard_data.objects.filter(user_id = i,is_sample=True).delete()
        # Call the import_data command with the user_id
        # try:
        #     call_command('sample_dashboard', i, server.id)
        #     # call_command('sample_dashboard2', i)
        #     call_command('sample_dashboard3', i, server.id)
        #     call_command('sample_dashboard4', i, server.id)
        #     call_command('sample_dashboard5', i, server.id)
        # except Exception as e:
        #     pass
        # Call the import_data command with the user_id
        thread = threading.Thread(target=authentication.signup_thread, args=(i,))
        thread.start()
    return HttpResponse("Success")

class SignupWithoutOTP(CreateAPIView):
    serializer_class= register_serializer

    @transaction.atomic()
    @csrf_exempt
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            u=serializer.validated_data['username']
            email = serializer.validated_data['email']
            pwd=serializer.validated_data['password']
            cnfpwd=serializer.validated_data['conformpassword']
            if (UserProfile.objects.filter(username=u).exists()):
                return Response({"message": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif len(u)>30:
                return Response({"message": "usernme allows upto 30 characters only"}, status=status.HTTP_400_BAD_REQUEST)
            elif (UserProfile.objects.filter(email=email).exists()):
                return Response({"message": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"

            r= re.findall(pattern,pwd)
            if not r:
                return Response({"message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."},status=status.HTTP_406_NOT_ACCEPTABLE)
            if pwd!=cnfpwd:
                return Response({"message":"Password did not matched"},status=status.HTTP_406_NOT_ACCEPTABLE)

            try:
                unique_id = get_random_string(length=64)
                
                adtb=UserProfile.objects.create_user(
                    username=u,
                    name=u,
                    password=pwd,
                    email=email,
                    is_active=True,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    demo_account = True
                    )
                try:
                    rlmd=Role.objects.get(role='Admin')
                except:
                    prev=previlages.objects.all().values()
                    pr_ids=[i1['id'] for i1 in prev]
                    rlmd=Role.objects.create(role='Admin',role_desc="All previlages",previlage_id=pr_ids)
                UserRole.objects.create(role_id=rlmd.role_id,user_id=adtb.id)
                user_id=adtb.id
                # Call the import_data command with the user_id
                thread = threading.Thread(target=authentication.signup_thread, args=(user_id,))
                thread.start()
                # try:
                #     call_command('sample_dashboard', adtb.id)
                #     # call_command('sample_dashboard2', adtb.id)
                #     call_command('sample_dashboard3', i, server.id)
                #     call_command('sample_dashboard4', i, server.id)
                #     call_command('sample_dashboard5', i, server.id)
                # except Exception as e:
                #     return Response({"message":str(e)},status=status.HTTP_406_NOT_ACCEPTABLE)
                
                data = {
                    "message" : "Registration successful! Please log in.",
                    # "email" : email.lower(),
                    # "emailActivationToken"  : unique_id
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except:
                return Response({"message":f"SMTP Error"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({"message":"Serializer Value Error"},status=status.HTTP_400_BAD_REQUEST)  