from oauth2_provider.models import Application,AccessToken,RefreshToken
import datetime
from pytz import utc
from dashboard.models import *
from django.conf import settings
import requests
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from sqlalchemy import create_engine, inspect, MetaData, Table, text,insert
from sqlalchemy.exc import OperationalError
import json,os
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
import boto3
import ast
import re
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Float, Date, Time, DateTime, Numeric,TIMESTAMP,VARCHAR,BIGINT,SMALLINT,CHAR,Text,TEXT,VARBINARY
from .views import test_token,encode_string
from collections import Counter
from django.views.decorators.csrf import csrf_exempt
import io
from dashboard.columns_extract import server_connection
from .Connections import file_save_1
from dashboard import roles,previlages,columns_extract,Connections
from quickbooks import models as qb_models
import sqlglot
from urllib.parse import quote
import numpy as np
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from django.core.paginator import Paginator
import copy
from sqlglot import transpile
from django.db.models import Q
from .clickhouse import Clickhouse
from quickbooks import models
import random
import string




created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)

def pagination(request,data,page_no=1,page_count=10):
    try:	
        paginator = Paginator(data,page_count)
        page = paginator.page(request.GET.get("page", page_no))
        data1 = {
            'status':200,
            'data':page.object_list,
            "total_pages":paginator.num_pages,
            "items_per_page":page_count,
            "total_items":paginator.count
        }
    except Exception as e:
        data1 = {
            "status":400,
            "message":str(e)
        }
    return data1

integer_list=['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double','int64','int32','float64','float32','nullable(int64)', 'nullable(int32)', 'nullable(uint8)', 
    'nullable(float(64))','int8','int16','int32','int64','float32','float16','float64','decimal(38,10)','decimal(12,2)','uuid','nullable(int8)','nullable(int16)','nullable(int32)','nullable(int64)','nullable(float32)','nullable(float16)','nullable(float64)','nullable(decimal(38,10)','nullable(decimal(12,2)']
char_list=['varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying','string','str','nullable(varchar)', 'nullable(bp char)', 'nullable(text)', 
    'nullable(varchar2)', 'nullable(NVchar2)', 
    'nullable(long)', 'nullable(char)', 'nullable(Nchar)', 
    'nullable(character varying)', 'nullable(string)','string','nullable(string)','array(string)','nullable(array(string))']
bool_list=['bool','boolean','nullable(bool)', 'nullable(boolean)','uint8']
date_list=['date','time','datetime','datetime64(6)','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone','timestamptz','nullable(date)', 'nullable(time)', 'nullable(datetime)', 
    'nullable(timestamp)', 
    'nullable(timestamp with time zone)', 
    'nullable(timestamp without time zone)', 
    'nullable(timezone)', 'nullable(time zone)', 'nullable(timestamptz)', 
    'nullable(datetime)','datetime64','datetime32','date32','nullable(date32)','nullable(datetime64)','nullable(datetime32)','date','datetime','time','datetime64','datetime32','date32','nullable(date)','nullable(time)','nullable(datetime64)','nullable(datetime32)','nullable(date32)'] 


date_list11=['date','timestamp without time zone'] 
timestamp_list = ['time','datetime','timestamp','timestamp with time zone','timezone','time zone','timestamptz']

def date_format(date_format_str, data_type):
    return {
        'year': '%Y', 'month': '%m', 'day': '%d', 'hour': '%H', 
        'minute': '%i', 'second': '%S', 'week numbers': '%V', 
        'weekdays': '%w', 'month/year': '%m/%Y', 
        'month/day/year': '%m/%d/%Y', 'year/month/day': '%Y/%m/%d',
        'quarter': 'quarter'
    }.get(date_format_str.lower(), '%m/%d/%Y' if data_type in date_list else '%Y/%m/%d %H:%M:%S')

def execution_query(query,cur,dbtype):
    try:
        if dbtype.lower() =='microsoftsqlserver':
            result_proxy = cur.execute(query)
            col =[des[0] for des in cur.description]
        else:
            result_proxy = cur.execute(text(query))
            col=[des[0] for des in result_proxy.cursor.description]
        result = {
        "status":200,
        "results_data":result_proxy,
        "columns":col
        }
    except SQLAlchemyError as e:
        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
        main_error_line = error_message.splitlines()[0]  # Get the main error line
        result = {
            "status":400,
            "message":main_error_line
        }
    except Exception as e:
        main_error_line = str(e).splitlines()[0]  # Get the main error line
        result = {
            "status": 400,
            "message": main_error_line
        }
    
    return result


def dtype_fun(dtype):
    a = {'postgresql':'postgres','oracle':'oracle','mysql':'mysql','sqlite':'sqlite','microsoftsqlserver':'tsql','snowflake':'snowflake','clickhouse':'clickhouse'}
    if a[dtype]:
        res = a[dtype]
    else:
        res = 'invalid datatype'
    return res

def query_parsing(read_query,use_l,con_l): 
    try:
        use = dtype_fun(use_l)
        con = dtype_fun(con_l)
        if use.lower() =='tsql':
            query = "{}".format(read_query)
        else:
            pass
        use_q = sqlglot.parse_one(read_query,read=use)
        con_q = use_q.sql(con)
        return con_q
    except Exception as e:
        print(e)


def map_dtype(dtype):
    dtype_mapping = {
        pd.api.types.is_integer_dtype: 'Int64',
        pd.api.types.is_float_dtype: 'Float64',
        pd.api.types.is_bool_dtype: 'boolean',
        pd.api.types.is_datetime64_any_dtype: 'datetime64[ns]',
    }
    for check, dtype_str in dtype_mapping.items():
        if check(dtype):
            return dtype_str
    return 'string'
    
def read_excel_file_data(file_path,filename,joining_tables,check):
    try:
        encoded_url = quote(file_path, safe=':/')
        xls = pd.ExcelFile(encoded_url)
        l=[]
        sheet_name = []
        BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
        db_file_path = os.path.join(BASE_DIR, 'local.db')
        url = f'sqlite:///{db_file_path}'
        engine = create_engine(url)
        tables = tables_get(joining_tables)
        if check==False:
            for i in xls.sheet_names:
                if i in tables:
                    data_csv = pd.read_excel(xls,sheet_name=i)
                    data_csv = data_csv.fillna(value='NA')
                    sheet_name.append(i)
                    for column in data_csv.columns:
                        non_null_data = data_csv[column]
                        if not non_null_data.empty:
                            dtype = non_null_data.dtype
                            mapped_dtype = map_dtype(dtype)
                            data_csv[column] = data_csv[column].astype(mapped_dtype)
                    
                    data_csv.to_sql(i, engine, index=False, if_exists='replace')
                else:
                    pass
        else:
            for i in xls.sheet_names:
                data_csv = pd.read_excel(xls,sheet_name=i)
                data_csv = data_csv.fillna(value='NA')
                sheet_name.append(i)
                for column in data_csv.columns:
                    non_null_data = data_csv[column]
                    if not non_null_data.empty:
                        dtype = non_null_data.dtype
                        mapped_dtype = map_dtype(dtype)
                        data_csv[column] = data_csv[column].astype(mapped_dtype)
                
                data_csv.to_sql(i, engine, index=False, if_exists='replace')
                
        f_dt = {
            "status":200,
            "engine":engine,
            "cursor":engine.connect(),
            "tables_names":sheet_name
        }
        return f_dt
    except Exception as e:
        f_dt = {
            "status":400,
            "message":e
        }
        return f_dt


def read_csv_file_data(file_path,filename,check):
    try:
        data_csv = pd.read_csv(file_path,low_memory=False)
        data_csv = data_csv.fillna(value='NA')
        for column in data_csv.columns:
                non_null_data = data_csv[column]
                if not non_null_data.empty:
                    dtype = non_null_data.dtype
                    mapped_dtype = map_dtype(dtype)
                    data_csv[column] = data_csv[column].astype(mapped_dtype)

        BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
        db_file_path = os.path.join(BASE_DIR, 'local.db')
        url = f'sqlite:///{db_file_path}'
        engine = create_engine(url)
        data_csv.to_sql(filename, engine, index=False, if_exists='replace')
        f_dt = {
                "status":200,
                "engine":engine,
                "cursor":engine.connect(),
                "tables_names":[filename]
            }
        return f_dt
    except Exception as e:
        f_dt = {
            "status":400,
            "message":e
        }
        return f_dt
    
def server_details_check(ServerType1,server_details,file_type,file_data,check):
    if file_type is None or  file_data =='' or file_data is  None or file_data =='':
        server_conn=server_connection(server_details.username,server_details.password,server_details.database,server_details.hostname,server_details.port,server_details.service_name,ServerType1.server_type.upper(),server_details.database_path)
        if server_conn['status']==200:
            engine=server_conn['engine']
            cursor=server_conn['cursor']
            data = {
                'status':200,
                'engine':engine,
                'cursor':cursor,
                'tables':[]
            }
        else:
            data = {
                'status':server_conn['status'],
                'message':server_conn
            }
    elif file_type is not None or  file_data !='' or file_data is not  None or file_data !='':
        clickhouse_class = Clickhouse(file_data.display_name)
        data = {
                'status':200,
                'engine':clickhouse_class.engine,
                'cursor':clickhouse_class.engine.connect(),
                'tables':[]
            }
    else:
        data = {
            'status':400,
            'message':'no Data'
        }
        
    return data

    

def relation(tables,table_col,dbtype):
    try:
        list_of_tables={}
        list_of_tables1={}
        for i in range(len(tables)):
            table1 = []
            table2 =[]
            for j in table_col:
                if tables[i] == j[0]:
                    table1.append(f'{j[1]}:{j[2]}')
                    table2.append(f'{j[1]}')
            list_of_tables[tables[i]] = table1 
            list_of_tables1[tables[i]] = table2
        dynamic_con = [] 
        comp = [i for i in range(1,len(tables))]
        relation_tables= []
        for i in range(0,len(tables)):
            for j in range(i+1,len(tables)):
                if i<j and j  in comp:
                    lisst = list_of_tables[tables[i]]
                    liset = list_of_tables[tables[j]]
                    dict1 = {item.split(':')[0]: item for item in lisst}
                    dict2 = {item.split(':')[0]: item for item in liset}
                    intersection_list = list(set(dict1.keys())& (set(dict2.keys()))) 
                    final_data =[]
                    for name in intersection_list:
                        if name in dict1:
                            final_data.append(dict1[name])
                        if name in dict2:
                            final_data.append(dict2[name])
                    if intersection_list:
                        jj = (tables[i],tables[j])
                        relation_tables.append(jj)
                        if j in comp:
                            comp.remove(j)
                            sorted_strings_list =  sorted(final_data, key=lambda x: x.split(':')[1].lower() not in integer_list)
                            aa= [s.split(':')[0] for s in sorted_strings_list]
                            formast = tables[i].split(' ')
                            formaet = tables[j].split(' ')
                            if dbtype.lower()=='snowflake':
                                string = [f'{formast[1]}.{aa[0]} = {formaet[1]}.{aa[0]}']
                            else:
                                string = [f'{formast[1]}.\"{aa[0]}\" = {formaet[1]}.\"{aa[0]}\"']
                            string = [query_parsing(string[0],'sqlite',dbtype)]
                            if len(dynamic_con)>j:
                                dynamic_con.append(string)
                            else:
                                dynamic_con.insert(j-1,string)
                        else:
                            pass
                    else:
                        pass
        response_data = {
                "status" : 200,
                "relation":relation_tables,
                "conditions":dynamic_con,
                "comp" : comp

        }
    except Exception as e:
         response_data = {
                "status" : 404,
                "message" : str(e)

        }
    return response_data




def building_query(self,tables,join_conditions,join_types,engine,dbtype):
    table_col= []
    alias_columns = []
    try:
        for schema,table_name,alias in tables:
            metadata = MetaData()
            if dbtype == 'microsoftsqlserver':
                qu =f"""
                    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                    AND TABLE_SCHEMA = '{schema}'
                """
                cursor = engine.cursor()
                cursor_query_data = execution_query(qu,cursor,dbtype.lower()) 
                if cursor_query_data['status'] == 200:
                    a1 = cursor_query_data['results_data']
                else:
                    return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                
                columns = [{'name':column.COLUMN_NAME,'col':str(column.DATA_TYPE)} for column in a1.fetchall()]
            else:
                table = Table(table_name, metadata,autoload_with =engine,schema = schema)
                columns= [{'name':column.name,'col':str(column.type)} for column in table.columns]
            for column in columns:
                if dbtype.lower()=='snowflake':
                    a =r'{}.{} "{}"'.format(schema,table_name,alias)
                else:
                    a =r'"{}"."{}" "{}"'.format(schema,table_name,alias)
                alias_columns.append(f"\"{alias}\".\"{column['name']}\"")
                table_col.append((f'{a}',column['name'],column['col'].lower()))
    except Exception as e:
        return_data = {
            "status":400,
            "message" : f'{e}  table not present in databse'
        }
        return return_data
    if dbtype.lower()=='snowflake':
        tables = [r'{}.{} "{}"'.format(schema,table,alias) for schema,table,alias in tables]
    else:
        tables = [r'"{}"."{}" "{}"'.format(schema,table,alias) for schema,table,alias in tables]
    table_json = []
    for j in tables:
        for i in range(len(table_col)):
            if j==table_col[i][0]:
                json_str = {"table":table_col[i][0],"col":table_col[i][1],"dtype":table_col[i][2]}
                table_json.append(json_str)
    
    query = f"SELECT * FROM {tables[0]}"
    join_types1=[]
    
    try:
        length_condition_val = 0
        for i in join_conditions:
            if len(i)>0:
                length_condition_val+=1
            else:
                break
        if len(tables)-1==length_condition_val:
            
            try:
                for i in range(1, len(tables)):
                    if i-1 < len(join_types):
                        join_type = join_types[i-1]
                    else :
                        join_type = 'inner' 
                    join_types1.append(join_type)
                    query+=f" {join_type} JOIN {tables[i]}"
                    for index,user_cond in enumerate(join_conditions[i-1]):
                        if dbtype.lower()=='snowflake':
                            cond1,cond2 = user_cond.split('=')
                            one,two = cond1.split('.')
                            three,four = cond2.split('.')
                            cond1 = one+'.'+two.replace('"','')
                            cond2 = three+'.'+four.replace('"','')
                            user_cond = cond1+' = '+cond2
                            join_conditions[i-1][index] = user_cond
                        else:
                            
                            user_cond=user_cond
                        if index==0:
                            query += f"  ON {user_cond}"
                        else:
                             query += f"  AND {user_cond}"
            except Exception as e:
                error_data = {
                "status":400,
                "message" :str(e)
                }
                return error_data        
        else:
            get_data = relation(tables,table_col,dbtype)
            if get_data['status'] ==200:
                pass
            else:
                return {"message" : get_data['message']}
            comp = get_data['comp']
            relation_tables = get_data['relation']
            dynamic_cond = get_data['conditions']
            no_relation_tables =[]
            my_relation_tables=[]
            if comp:
                for i in comp:
                    if i>=len(join_conditions):
                        schema_table,table_name = tables[i].split(' ')
                        no_relation_tables.append(table_name)
                    else:
                        for user_cond in join_conditions:
                            try:
                                if len(user_cond)>=1:
                                    match = tables[i].split(' ')[1]
                                    cond1,cond2 = user_cond[0].replace("'",'').split('=')
                                    one,two = cond1.split('.')
                                    three,four = cond2.split('.')
                                    cond1 = one+'.'+two.replace('"','')
                                    cond2 = three+'.'+four.replace('"','')
                                    if match==one.strip() or match==three.strip():
                                        k=''
                                        one1=''
                                        three1=''
                                        for table in tables:
                                            if one in table:
                                                one1 += table
                                            elif three in table:
                                                three1 += table
                                            else:
                                                pass
                                        k=(one1,three1)
                                        relation_tables.insert(i-1,k)                                  
                                    else:
                                        pass

                                else:
                                    pass
                            except Exception as e:
                                print(e)
                        
                    
            else:
                pass
            if  no_relation_tables!=[] : 

                return_data = {
                    "status":204,   
                    "relation" : join_conditions,
                    "no_relation":no_relation_tables
                    }
                return return_data
            
            else:    
                my_relation_tables = relation_tables
                condition = {}
                for i in range(len(my_relation_tables)):
                    ll1= []
                    if join_conditions[i]:
                        a = join_conditions[i]
                    else:
                        a = dynamic_cond[-1]
                        join_conditions[i].append(a[0])
                    ll1.append(a)
                    key = my_relation_tables[i]
                    condition[key] = ll1
                for i in range(0, len(tables)):
                    key_data = list(condition.keys())
                    compare_value = key_data[i-1]
                    for j in range(0,len(key_data)):
                        if (tables[i-1],tables[j+1]) in(condition):
                            if j < len(join_types):
                                join_type = join_types[j-1]
                            else :
                                join_type = 'inner' 
                            join_types1.append(join_type)
                            query+= f' {join_type} join {tables[j+1]}'
                            if len(condition[compare_value])>=1:
                                for index,cond in enumerate(condition[compare_value]):
                                    if index ==0:
                                        query+= f' on {cond[0]}'
                                    else:
                                        query+= f" and {cond[0]} " 
                                             
    except Exception as e:
        error_data = {

        "status":400,
        "message" :f'{e}'
            }
        return error_data
    return_data ={
    "status" :200,
    "query_data" : query,
    "joining" : join_conditions,
    "tables" :table_json,
    "join_types" : join_types1,
    "make_columns":alias_columns
        
    }
    return return_data


def connection_data_retrieve(hierarchy_id,user_id):
    parent_id = parent_ids.objects.get(id=hierarchy_id)
    match parent_id.parameter:
        case 'server':
            conn_data = ServerDetails.objects.get(user_id = user_id, id=parent_id.table_id)
            conn_type = ServerType.objects.get(id = conn_data.server_type).server_type
            serdt=server_connection(conn_data.username,conn_data.password,conn_data.database,conn_data.hostname,conn_data.port,conn_data.service_name,conn_type.upper(),conn_data.database_path)            
            if serdt['status']==200:
                
                
                click = Clickhouse(conn_data.display_name)
                result = {
                    "status":200,
                    "engine":click.engine,
                    "cursor":click.cursor,
                    "conn":'clickhouse'
                }
            else:
                return  {
                    "status":400,
                    "message":serdt['message']        }
            
        case 'files':
            if FileDetails.objects.filter(id=parent_id.table_id).exists:
                conn_data = FileDetails.objects.get(id=parent_id.table_id)
                
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'quickbooks':
            if models.TokenStoring.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.TokenStoring.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'salesforce':
            if models.TokenStoring.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.TokenStoring.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'halops':
            if models.HaloPs.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.HaloPs.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'connectwise':
            if models.connectwise.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.connectwise.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'shopify':
            if models.Shopify.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.Shopify.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
        case 'google_sheets':
            if models.TokenStoring.objects.filter(id=parent_id.table_id).exists:
                conn_data =models.TokenStoring.objects.get(id=parent_id.table_id)
                click = Clickhouse(conn_data.display_name)
                result = {
                        "status":200,
                        "engine":click.engine,
                        "cursor":click.cursor,
                        "conn":'clickhouse'
                    }
            else:
                result = {
                        "status":400,
                        'message':'DATA NOT FOUND'
                    }
    return result



def tables_get(joining_tables):
    tables=[]
    for i in joining_tables:
        tables.append(i[1])
    return tables



def connection_setup(server_id,file_id,user_id,query_id): 
    con_data =connection_data_retrieve(server_id,file_id,user_id)
    if con_data['status'] ==200:                
        ServerType1 = con_data['serverType1']
        server_details = con_data['server_details']
        file_type = con_data["file_type"]
        file_data =con_data["file_data"]
        dbtype = con_data['dbtype']
    else:
        return  {
            "status":400,
            "message":con_data['message']        }
    query_data2 = QuerySets.objects.get(queryset_id = query_id,user_id = user_id)
    serdt=server_details_check(ServerType1,server_details,file_type,file_data,False)
    if serdt['status']==200:
        
        result = {
            "status":200,
            "engine":serdt['engine'],
            "cursor":serdt['cursor'],
            "dbtype":dbtype.lower()
        }
    else:
        return  {
            "status":400,
            "message":serdt['message']        }
    return result

class rdbmsjoins(CreateAPIView):
    serializer_class = tablejoinserializer
    @transaction.atomic
    @csrf_exempt
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            user_id = tok1['user_id']
            if serializer.is_valid(raise_exception=True):
                hierarchy_id = serializer.validated_data['hierarchy_id']
                query_set_id = serializer.validated_data['query_set_id']
                joining_tables = serializer.validated_data['joining_tables']
                join_type = serializer.validated_data['join_type']
                join_table_conditions= serializer.validated_data['joining_conditions']
                dragged_array = serializer.validated_data['dragged_array']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT) 
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            
            
            if len(joining_tables) ==0:
                Response_data= {
                        "query_set_id" : 0,
                        "relation_btw_tables": [],
                        'joining_condition': [],
                        'tables_col' :[],
                        "join_types": [],
                        "joining_condition_list" : []
                                }
                Connections.delete_data(query_set_id,query_set_id,tok1['user_id'])
                QuerySets.objects.filter(queryset_id = query_set_id).delete()
                return JsonResponse({"message":"Joining tables successfully","table_columns_and_rows":Response_data},status=status.HTTP_200_OK,safe=False)
            else:
                for index,i in enumerate(join_table_conditions):
                    for index1,j in enumerate(i):
                        if j:
                            new_cond = query_parsing(j,'sqlite',conn_type)
                            join_table_conditions[index][index1] = new_cond
                        else:
                            pass
                responce = building_query(self,joining_tables,join_table_conditions,join_type,engine,conn_type)
                try:
                    if responce['status']==200:
                        query1 = responce['query_data']                        
                    elif responce["status"] ==400:
                        return Response({'message':responce["message"]},status=status.HTTP_400_BAD_REQUEST)
                    elif responce["status"]==204:
                        return Response({'message':f'No Relation Found {responce["no_relation"]}','joining_condition' :responce['relation']},status=status.HTTP_404_NOT_FOUND)
                    else:
                        pass
                    aa = alias_to_joins(responce['make_columns'],conn_type)
                    column_list11 = ','.join(aa)
                    
                    query1 = query1.replace('*',column_list11)
                    converted_query = query_parsing(query1,'sqlite',conn_type)
                    
                    
                    query_set_id = query_set_id if query_set_id else 0
                    file_path = file_save_1(dragged_array,hierarchy_id,query_set_id,'datasource',"")
                    try:
                        if conn_type.lower() =='microsoftsqlserver':
                            result_proxy = cur.execute(converted_query)
                        else:
                            result_proxy = cur.execute(text(converted_query))
                    except SQLAlchemyError as e:
                        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
                        main_error_line = error_message.splitlines()[0]  # Get the main error line
                        return Response({'message':main_error_line},status = status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        main_error_line = str(e).splitlines()[0]  # Get the main error line
                        return Response({'message':main_error_line},status = status.HTTP_400_BAD_REQUEST)
                    if query_set_id is None or query_set_id==0:
                        a = QuerySets.objects.create(
                            user_id = user_id,
                            hierarchy_id = hierarchy_id,
                            table_names = joining_tables,
                            join_type = responce['join_types'],
                            joining_conditions  = responce['joining'],
                            custom_query = converted_query,
                            datasource_path = file_path['file_key'],
                            datasource_json = file_path['file_url'],
                            created_at=datetime.datetime.now(utc),
                            updated_at=datetime.datetime.now(utc)
                            
                        )
                        id = a.queryset_id
                        QuerySets.objects.filter(queryset_id=a.queryset_id).update(created_at=created_at,updated_at=updated_at)
                    else:
                        a = QuerySets.objects.filter(queryset_id = query_set_id).update(
                            user_id = user_id,
                            hierarchy_id = hierarchy_id,
                            table_names = joining_tables,
                            join_type = responce['join_types'],
                            joining_conditions  = responce['joining'],
                            custom_query = converted_query,
                            datasource_path = file_path['file_key'],
                            datasource_json = file_path['file_url'],
                            updated_at=datetime.datetime.now(utc)
                            
                        )
                        id = query_set_id
                        QuerySets.objects.filter(queryset_id=query_set_id).update(updated_at=updated_at)
                    joining_condition_list=[]
                    join_types_list= responce['join_types']
                    if len(responce['joining'])>0:
                        for index,i in enumerate(responce['joining']):   
                            for j in i:
                                joining_condition_list.append({'condition':j,'type':join_types_list[index]})
                    else:
                        pass
                    Response_data= {
                        "hierarchy_id": hierarchy_id,
                        "query_set_id" : id,
                        'joining_condition': responce['joining'],
                        'tables_col' :responce['tables'],
                        "join_types": responce['join_types'],
                        "joining_condition_list" : joining_condition_list
                                }
                except Exception as e:
                    return Response({"message":f'{e}'},status=status.HTTP_400_BAD_REQUEST)
            cur.close()
            return JsonResponse({"message":"Joining tables successfully","table_columns_and_rows":Response_data},status=status.HTTP_200_OK,safe=False)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
      
def delete_tables_sqlite(cur,engine,tables):
    
    try:
        with cur as connection:
            if len(tables) > 0:
                for table in tables:
                    drop_table_sql = text(f'DROP TABLE IF EXISTS \"{table}\";')
                    connection.execute(drop_table_sql)
            connection.commit()
    except Exception as e:
        print(e)
                  
import math
def replace_nan_with_none(value):
    return None if isinstance(value, float) and math.isnan(value) else value


def get_clean_data(data):
    clean_data = [
        [None if (isinstance(value, float) and (math.isnan(value) or math.isinf(value))) else value for value in row]
        for row in data
    ]
    return clean_data

class joining_query_data(CreateAPIView):
    serializer_class = queryserializer
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                query_id= serializer.validated_data['query_id']
                row_limit = serializer.validated_data['row_limit']
                datasource_queryset_id  = serializer.validated_data['datasource_queryset_id']
                hierarchy_id = serializer.validated_data['hierarchy_id']

            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            user_id = tok1['user_id']
            if query_id == '0':
                data={
                "column_data" : [],
                'row_data' : [],
                "query_exection_time":0.00,
                "no_of_rows":0,
                "no_of_columns":0
                }
                return Response(data,status=status.HTTP_200_OK) 
            else:
                
                con_data =connection_data_retrieve(hierarchy_id,user_id)
                if con_data['status'] ==200:                
                    engine=con_data['engine']
                    cur=con_data['cursor']
                    conn_type = con_data['conn']
                else:
                    return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                try:
                    query_data2 = QuerySets.objects.get(queryset_id = query_id,user_id = user_id)
                except:
                    return Response({'message':'Data Not Found'},status = status.HTTP_404_NOT_FOUND)
                try:
                    if datasource_queryset_id is None:
                        query_data = QuerySets.objects.get(queryset_id = query_id,user_id = user_id)
                        query_name=query_data.query_name
                    else:
                        query_data = DataSource_querysets.objects.get(datasource_querysetid = datasource_queryset_id,user_id = user_id,queryset_id = query_id)
                        query_data1 = QuerySets.objects.get(queryset_id = query_id,user_id = user_id)
                        query_name=query_data1.query_name
                except:
                    return Response({'message':'Data not found'},status=status.HTTP_400_BAD_REQUEST)
                st=datetime.datetime.now(utc)
                query_count=query_data.custom_query
                if 'limit' in str(query_data.custom_query).lower():
                    query=query_data.custom_query 
                else:
                    query = query_data.custom_query + f' limit {row_limit} '
                query = query_parsing(query,conn_type,conn_type)
                cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                if cursor_query_data['status'] == 200:
                    result_proxy = cursor_query_data['results_data']
                else:
                    return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                query_result = result_proxy.fetchall()
                column_names = cursor_query_data['columns']
                pattern = r'(?i)(select\s+)(.*?)(\s+from\s+)'
                modified_query = re.sub(pattern, r'\1COUNT(*)\3', query_count, count=1)
                count_result = execution_query(modified_query,cur,conn_type.lower()) 
                if count_result['status'] == 200:
                    qr_rest = count_result['results_data']
                else:
                    return Response({"message":count_result['message']},status=status.HTTP_404_NOT_FOUND) 
                rl_count =qr_rest.fetchall()  
                et=datetime.datetime.now(utc)
                
                response_data =get_clean_data(query_result)
                if query_name is None or query_name =="":
                    en_str=encode_string(str(query_id))
                    query_name=str('Untitled_')+str(en_str)
                    # query_name = 'Untitled' + ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                data={
                    "hierarchy_id": hierarchy_id,
                    "query_set_id" : query_data.queryset_id, 
                    "queryset_name":query_name,
                    "custom_query" :query,
                    "column_data" : column_names,
                    'row_data' : response_data,
                    "is_custom_query":query_data.is_custom_sql,
                    "query_exection_time":et-st,
                    "total_rows":rl_count[0][0],
                    "no_of_rows":len(response_data),
                    "no_of_columns":len(column_names),
                    "created_at":query_data.created_at,
                    "updated_at":query_data.updated_at,
                    "query_exection_st":st.time(),
                    "query_exection_et":et.time()
                }
                cur.close()
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)



def get_sqlalchemy_type(type_code):
    type_code_map ={
        16: Boolean,
        20: Integer,  # BIGINT in SQLAlchemy is equivalent to Integer in PostgreSQL
        21: Integer,  # SMALLINT in SQLAlchemy is equivalent to Integer in PostgreSQL
        23: Integer,
        700: Float,
        701: Float,
        1700: Numeric,
        1082: Date,
        1083: Time,
        1114: TIMESTAMP,  # TIMESTAMP WITHOUT TIME ZONE in SQLAlchemy is equivalent to DateTime in PostgreSQL
        1184: TIMESTAMP,  # TIMESTAMP WITH TIME ZONE in SQLAlchemy is equivalent to DateTime in PostgreSQL
        1043: String,  # VARCHAR in SQLAlchemy is equivalent to String in PostgreSQL
        127: BIGINT,      # bigint
        52: SMALLINT,
        175: CHAR,        # char
        239: String,      # nchar
        35: TEXT,         # text
        99: TEXT,         # ntext
        173: VARBINARY,   # binary
        165: VARBINARY,
        17: String,
    }
    if isinstance(type_code,int):
        value =type_code_map.get(type_code, String)()
    else:
        value = type_code
    return value


from decimal import Decimal
class Sqlite3_temp_table():
    def __init__(self,main_query,dbtype):
        self.BASE_DIR = settings.BASE_DIR
        self.db_file_path = os.path.join(self.BASE_DIR, 'db.sqlite3')
        self.engine = sqlite3.connect(self.db_file_path)
        self.cur = self.engine.cursor()
        self.main_query = main_query
        self.dbtype = dbtype
    def create(self,result_column_values,results,table):
        try:
            if self.dbtype =='microsoftsqlserver':
                column11 =''
                insertvalues = ''
                for i in result_column_values:
                    column11 += f'\"{i[0]}\" {i[1].__name__},'
                    insertvalues += '?,'
            else:
                column11 =''
                insertvalues = ''
                for i in result_column_values:
                    column11 += f'\"{i[0]}\" {get_sqlalchemy_type(i[1])},'
                    insertvalues += '?,'
            create_query = f"CREATE TABLE  {table} ( {column11.rstrip(',')})"
            convert_create_query = query_parsing(create_query,self.dbtype,'sqlite')
            try:
                metadata = MetaData()
                bb= self.cur.execute(create_query)
                self.engine.commit()
                max_res =[]
                for values in results:
                    formatted_values = [float(value) if isinstance(value, Decimal) else value for value in values]
                    max_res.append(formatted_values)
                a1 = self.cur.executemany(f"INSERT INTO {table} VALUES ({insertvalues.rstrip(',')})", max_res)
                self.engine.commit()
            except sqlite3.Error as e:
                self.engine.rollback()
                self.delete(table)
                self.create(result_column_values,results,table)
          
            response = {
                'status': 200,
                "message" : 'table_created'
            }
        except Exception as e:
            response = {
                "status":400,
                'message':str(e)
            }
        return response
         
    def query(self,query):
        try:
            st = datetime.datetime.now(utc)
            res = self.cur.execute(query)
            et = datetime.datetime.now(utc)
            result_data= res.fetchall()
            response ={
            "status": 200,
            "columns":[description[0] for description in res.description],
            "results_data" : result_data,
            "st" : st,
            "et" :et
            }
        except Exception as e:
            response ={
            "status": 400,
            "message" : str(e)
            }
        return response
    
    def delete(self,table):
        try:
            a= self.cur.execute(f'DROP TABLE IF EXISTS "{table}";')
            self.engine.commit()
            response ={
            "status": 200,
            "message" : 'deleted'
            }
        except Exception as e:
            response ={
            "status": 400,
            "message" : str(e)
            }
        return response



class Duplicate_sheet_filters(CreateAPIView):
    @transaction.atomic()
    def get(self,request,sheet_id,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_sheet_filters])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            sheet_filter_id = sheet_data.objects.get(id = sheet_id).filter_ids
            sheet_filter_id = literal_eval(sheet_filter_id)
            filter_return_id= []
            if sheet_filter_id:
                for filter_1 in sheet_filter_id:
                    filter_data = ChartFilters.objects.get(filter_id = filter_1)
                    filter_data.filter_id=None
                    filter_save_id = filter_data.save()
                    filter_return_id.append({'id':filter_data.filter_id,'col_name':filter_data.col_name})

            else:
                pass
            return Response({'message':'Sheet Fiters Duplicated','filters_list':filter_return_id},status = status.HTTP_200_OK)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)




class Chart_filter(CreateAPIView):
    serializer_class = FilterSerializer
    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_sheet_filters])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                hierarchy_id = serializer.validated_data['hierarchy_id']
                type_of_filter = serializer.validated_data['type_of_filter']
                query_set_id =serializer.validated_data['query_set_id']
                datasource_queryset_id = serializer.validated_data['datasource_queryset_id']
                col_name = serializer.validated_data['col_name']
                data_type = serializer.validated_data['data_type']
                format_date = serializer.validated_data['format_date']
                search = serializer.validated_data['search']
                parent_user = serializer.validated_data['parent_user']
                field_logic = serializer.validated_data['field_logic']
                is_calculated =serializer.validated_data['is_calculated']
                
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            if parent_user is None or parent_user =='':
                user_id = tok1['user_id']
            else:
                user_id=parent_user
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            query_data1 = QuerySets.objects.get(queryset_id = query_set_id,user_id = user_id)
            try:
                if type_of_filter.lower() == 'datasource' :
                    table_name_for_temp = f"data_source_table{user_id}"
                    query_data = QuerySets.objects.get(queryset_id = query_set_id,user_id = user_id)
                    
                elif(type_of_filter.lower() == 'sheet'and datasource_queryset_id is not None):
                    table_name_for_temp = f'sheet_table{user_id}'
                    query_data = DataSource_querysets.objects.get( datasource_querysetid= datasource_queryset_id,user_id = user_id)                    
                else:
                    table_name_for_temp = f'sheet_table{user_id}'
                    query_data = QuerySets.objects.get(queryset_id = query_set_id,user_id = user_id)
                
            except Exception as e:
                return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)
            if query_data:
                data_sourse_string = f'select * from ({query_data.custom_query})temp'
            else:
                return Response({'message':'Query Set ID is not Present'},status = status.HTTP_400_BAD_REQUEST)
                
                       
            response = get_filter_column_data(data_sourse_string,col_name,format_date,data_type,cur,conn_type,field_logic)
            if response['status'] ==200:
                result_data = response['results_data']
            else:
                return Response({'message':response['message']},status = status.HTTP_400_BAD_REQUEST)
            if search !='' or search != None:
                result_data = [row for row in result_data if str(search).lower() in str(row).lower()]
            Response_data = {
                    "hierarchy_id":hierarchy_id,
                    "query_set_id":query_set_id,
                    "col_name":field_logic if is_calculated else col_name,
                    "dtype" : data_type,
                    "col_name":col_name,
                    "col_data" : literal_eval(result_data) if result_data != [""] else []
                }
            cur.close()
           
            
            return Response(Response_data,status=status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
    
    
    serializer_class2 = chartfilter_update_serializer
    @transaction.atomic
    def put(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_sheet_filters])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class2(data=request.data)
            if serializer.is_valid(raise_exception=True):
                
                type_of_filter = serializer.validated_data['type_of_filter']
                filter_id = serializer.validated_data['filter_id']
                hierarchy_id = serializer.validated_data['hierarchy_id']
                queryset_id = serializer.validated_data['queryset_id']
                datasource_querysetid = serializer.validated_data['datasource_querysetid']
                range_values= serializer.validated_data['range_values']
                select_values = serializer.validated_data['select_values']
                col_name  = serializer.validated_data['col_name']
                data_type = serializer.validated_data['data_type']
                format_date = serializer.validated_data['format_date']
                parent_user = serializer.validated_data['parent_user']
                is_exclude = serializer.validated_data['is_exclude']
                field_logic = serializer.validated_data['field_logic']
                is_calculated =serializer.validated_data['is_calculated']
                top_bottom = serializer.validated_data['top_bottom']

            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            if parent_user is None or parent_user =='':
                user_id = tok1['user_id']
            else:
                user_id=parent_user
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            query_data1 = QuerySets.objects.get(queryset_id = queryset_id,user_id = user_id)
            try:
                if  top_bottom is  None:
                    try:
                        if type_of_filter.lower() == 'datasource' :
                            table_name_for_temp = f"data_source_table{user_id}"
                            query_data = QuerySets.objects.get(queryset_id = queryset_id,user_id = user_id)
                            
                        elif(type_of_filter.lower() == 'sheet'and datasource_querysetid is not None):
                            table_name_for_temp = f'sheet_table{user_id}'
                            query_data = DataSource_querysets.objects.get( datasource_querysetid= datasource_querysetid,user_id = user_id)                    
                        else:
                            table_name_for_temp = f"data_source_table{user_id}"
                            query_data = QuerySets.objects.get(queryset_id = queryset_id,user_id = user_id)
                        
                    except Exception as e:
                        return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST) 
                    if query_data:
                        data_sourse_string = f'select * from ({query_data.custom_query})temp'
                    else:
                        return Response({'message':'Query Set ID is not Present'},status = status.HTTP_400_BAD_REQUEST)
                        
                        
                    response = get_filter_column_data(data_sourse_string,col_name,format_date,data_type,cur,conn_type,field_logic)
                    if response['status'] ==200:
                        result_data = response['results_data']
                    else:
                        return Response({'message':response['message']},status = status.HTTP_400_BAD_REQUEST)
                else:
                    result_data=None
                if filter_id is not None:
                    if type_of_filter.lower() != 'datasource':
                        aaa = ChartFilters.objects.get(filter_id =filter_id)
                        if range_values:
                            aa = ChartFilters.objects.filter(filter_id =filter_id,user_id =user_id).update(filter_data = range_values,row_data = tuple(result_data),updated_at = datetime.datetime.now(),is_exclude = is_exclude,format_type = format_date)
                        elif top_bottom:
                            aa = ChartFilters.objects.filter(filter_id =filter_id,user_id =user_id).update(top_bottom = top_bottom,updated_at = datetime.datetime.now(),is_exclude = is_exclude,format_type=format_date)
                        else:
                            aa = ChartFilters.objects.filter(filter_id =filter_id,user_id =user_id  ).update(filter_data = tuple(select_values),row_data = tuple(result_data),updated_at = datetime.datetime.now(),is_exclude = is_exclude,format_type=format_date)
                    else:
                        aaa = DataSourceFilter.objects.get(filter_id =filter_id)
                        if range_values:
                            aa = DataSourceFilter.objects.filter(filter_id =filter_id,user_id =user_id ).update(filter_data = range_values,row_data = tuple(result_data),is_exclude = is_exclude,updated_at = datetime.datetime.now())
                        else:
                            aa = DataSourceFilter.objects.filter(filter_id =filter_id,user_id =user_id  ).update(filter_data = tuple(select_values),row_data = tuple(result_data),is_exclude = is_exclude,updated_at = datetime.datetime.now())
                    Response_data = {
                        "filter_id" : filter_id              
                    }
                else:
                    if type_of_filter.lower() == 'datasource':
                        if range_values:
                            aa = DataSourceFilter.objects.create(
                                    hierarchy_id = hierarchy_id,
                                    user_id=user_id,
                                    queryset_id =queryset_id,
                                    col_name = col_name,    
                                    data_type = data_type,
                                    filter_data = range_values,
                                    row_data = tuple(result_data),
                                    format_type = format_date,
                                    # is_exclude = is_exclude
                                )
                        else:
                            aa = DataSourceFilter.objects.create(
                                hierarchy_id = hierarchy_id,
                                user_id=user_id,
                                queryset_id =queryset_id,
                                col_name = col_name,    
                                data_type = data_type,
                                filter_data = tuple(select_values),
                                row_data = tuple(result_data),
                                format_type = format_date,
                                is_exclude = is_exclude
                            )
                    else:
                        if range_values:
                            aa = ChartFilters.objects.create(
                                    hierarchy_id=hierarchy_id,
                                    user_id=user_id,
                                    datasource_querysetid = datasource_querysetid,
                                    queryset_id  = queryset_id,
                                    col_name = col_name,    
                                    data_type = data_type,
                                    filter_data = range_values,
                                    row_data = tuple(result_data),
                                    format_type = format_date,
                                    is_exclude = is_exclude,
                                    field_logic = field_logic,
                                    is_calculated = is_calculated
                                )
                        elif top_bottom is not None:
                            aa = ChartFilters.objects.create(
                                    hierarchy_id=hierarchy_id,
                                    user_id=user_id,
                                    datasource_querysetid = datasource_querysetid,
                                    queryset_id  = queryset_id,
                                    col_name = col_name,    
                                    data_type = data_type,
                                    filter_data = None,
                                    row_data = None,
                                    format_type = format_date,
                                    is_exclude = is_exclude,
                                    field_logic = field_logic,
                                    is_calculated = is_calculated,
                                    top_bottom=top_bottom

                                )
                        else:
                            aa = ChartFilters.objects.create(
                                    hierarchy_id=hierarchy_id,
                                    user_id=user_id,
                                    datasource_querysetid = datasource_querysetid,
                                    queryset_id  = queryset_id,
                                    col_name = col_name,    
                                    data_type = data_type,
                                    filter_data = tuple(select_values),
                                    row_data = tuple(result_data),
                                    format_type = format_date,
                                    is_exclude = is_exclude,
                                    field_logic = field_logic,
                                    is_calculated = is_calculated

                                )

                    Response_data = {
                            "filter_id" : aa.filter_id              
                        }

            except Exception as e:
                print(str(e))
            cur.close()
            
            return Response(Response_data,status=status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        

def get_filter_column_data(data_sourse_string,col_name,format_date,data_type,cur,dbtype,field_logic):
    data_type = data_type.lower().replace('nullable(','')
    data_type = data_type.split('(')[0].replace(')','')
    if data_type.lower() in integer_list or data_type.lower()  in char_list  :
        query_string = data_sourse_string.replace('*',f' distinct(\"{col_name}\")',1) + ' order by 1'
        query_string = query_parsing(query_string,'sqlite',dbtype)
        query_result = execution_query(query_string,cur,dbtype.lower())                
        if query_result['status'] ==200:
            col_data = query_result['results_data']
        else:
            result_data = {
                'status':400,
                'message':query_result['message']
            }
        row_data =[]   
        for i in col_data:
            d1 = i[0]
            row_data.append(d1)
        result_data = row_data
    elif data_type.lower() in bool_list :
        query_string = data_sourse_string.replace('*',f' distinct(\"{col_name}\")',1) + ' order by 1'
        query_string = query_parsing(query_string,'sqlite',dbtype)
        query_result = execution_query(query_string,cur,dbtype.lower())   
        if query_result['status'] ==200:
            col_data = query_result['results_data']
        else:
            result_data = {
                            'status':400,
                            'message':query_result['message']
                        }  
            return result_data  
        row_data =[]   
        for i in col_data:
            d1 = i[0]
            if d1==0:
                row_data.append(False)
            elif d1==1:
                row_data.append(True)
            else:
                row_data.append(d1)
        result_data = row_data   
            
    elif 'aggregate' == data_type.lower() or data_type.lower() =='date_aggregate':
        if format_date.lower() =='count_distinct':
            query_string = data_sourse_string.replace('*',f" count(distinct \"{col_name}\")",1 )+ ' order by 1'
        else:
            query_string = data_sourse_string.replace('*',f" distinct({format_date}(\"{col_name}\"))",1 )+ ' order by 1'
        query_string = query_parsing(query_string,'sqlite',dbtype)
        query_result = execution_query(query_string,cur,dbtype.lower())
        if query_result['status'] ==200:
            col_data = query_result['results_data']
        else:
            result_data = {
                'status':400,
                'message':query_result['message']
            }
            return result_data
        result_data = []
        for i in col_data:
            result_data.append(i[0])
        
    elif data_type.lower() in date_list :
        query_string = data_sourse_string.replace('*',f" distinct({get_formatted_date_query('clickhouse',col_name,format_date)})",1) + ' order by 1'
        query_string = custom_date_transformation(query_string,dtype_fun(dbtype))
        query_string = query_parsing(query_string,'sqlite',dbtype)
        query_result = execution_query(query_string,cur,dbtype.lower())

        if query_result['status'] ==200:
            col_data = query_result['results_data']
        else:
            result_data = {
                'status':400,
                'message':query_result['message']
            }
            return result_data  
        result_data =[]   
        for i in col_data:
            d1 = i[0]
            result_data.append(d1) 
        result_data = date_data_change(format_date,result_data,1)
        result_data = literal_eval(result_data)
    elif data_type.lower() == 'calculated':
        query_string = data_sourse_string.replace('*',f"distinct({field_logic})",1) + ' order by 1'
        
        query_string = query_parsing(query_string,'sqlite',dbtype)
        query_result = execution_query(query_string,cur,dbtype.lower())
        if query_result['status'] ==200:
            col_data = query_result['results_data']
        else:
            result_data = {
                'status':400,
                'message':query_result['message']
            }
            return result_data  
        row_data =[]   
        for i in col_data:
            d1 = i[0]
            row_data.append(d1)
        result_data = row_data
       
    else:
        result_data = {
                'status':400,
                'message':'data error'
            }
        return result_data  
    result_data={
        'status':200,
        'results_data':result_data
    }
    return result_data




def get_formatted_date_query(db_type,date_column,f1):
    f1 = date_format(f1,db_type)
    if f1 =='%m' and db_type=='clickhouse':
        query = f""" CASE 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '01' THEN 'January' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '02' THEN 'February' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '03' THEN 'March' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '04' THEN 'April' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '05' THEN 'May' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '06' THEN 'June' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '07' THEN 'July' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '08' THEN 'August' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '09' THEN 'September' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '10' THEN 'October' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '11' THEN 'November' 
    WHEN DATE_FORMAT(\"{date_column}\", '%m') = '12' THEN 'December' 
    ELSE NULL 
  END """
    elif f1 =='%w':
        query= f""" CASE STRFTIME('%w',\"{date_column}\" )
                WHEN '7' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END """
    elif f1 =='count_distinct':
        if db_type == 'sqlite':
            query = f" count(Distinct STRFTIME('{f1}', \"{date_column}\"))"
        elif db_type =='clickhouse':
            query = f" count(Distinct DATE_FORMAT(\"{date_column}\",'{f1}'))"
        elif db_type == 'mysql':
            query = f" count(Distinct DATE_FORMAT(\"{date_column}\", '%Y-%m-%d')) "
        elif db_type == 'postgres':
            query = f" count(Distinct TO_CHAR({date_column}, 'YYYY-MM-DD'))  "
        elif db_type == 'sqlserver':
            query = f" count(Distinct FORMAT(\"{date_column}\", 'yyyy-MM-dd')) "
        elif db_type == 'oracle':
            query = f" count(Distinct TO_CHAR(\"{date_column}\", 'YYYY-MM-DD')) "
        else:
            raise ValueError("Unsupported database type")
    elif f1.lower()=='quarter':
        query = f"""CASE 
            WHEN date_format(\"{date_column}\", '%m') IN ('01', '02', '03') THEN 'Q1'
            WHEN date_format(\"{date_column}\", '%m') IN ('04', '05', '06') THEN 'Q2'
            WHEN date_format(\"{date_column}\", '%m') IN ('07', '08', '09') THEN 'Q3'
            WHEN date_format(\"{date_column}\", '%m') IN ('10', '11', '12') THEN 'Q4'
        END
            """
    else:
        if db_type == 'sqlite':
            query = f" STRFTIME('{f1}', \"{date_column}\")"
        elif db_type =='clickhouse':
            query = f" DATE_FORMAT(\"{date_column}\",'{f1}')"
        elif db_type == 'mysql':
            query = f" DATE_FORMAT(\"{date_column}\", '%Y-%m-%d') "
        elif db_type == 'postgres':
            query = f" TO_CHAR({date_column}, 'YYYY-MM-DD')  "
        elif db_type == 'sqlserver':
            query = f" FORMAT(\"{date_column}\", 'yyyy-MM-dd') "
        elif db_type == 'oracle':
            query = f" TO_CHAR(\"{date_column}\", 'YYYY-MM-DD') "
        else:
            raise ValueError("Unsupported database type")
    return query

    


def Custom_joining_filter(condition,chart_filter_data,type_of_db):
    p = literal_eval(chart_filter_data.filter_data)
    is_exclude = chart_filter_data.is_exclude
    # exclude_cond = 'IN'
    for_range = str(p).replace(',)',')')
    d111 =date_data_change(chart_filter_data.format_type,p,0)
    range_k = literal_eval(for_range) 
    table_name =re.search(r'\((.*?)\)', chart_filter_data.col_name)
    chart_filter_data.data_type = chart_filter_data.data_type.lower().replace('nullable(','').split('(')[0].replace(')','')
    input1 = chart_filter_data.filter_data
    formatted_input,contains_none_or_empty,none_check,is_empty_tuple = is_tuple_format(input1)
    col_name= chart_filter_data.col_name
    if is_exclude:
        # exclude_cond = ' NOT IN '
        if none_check or contains_none_or_empty:
            exclude_cond = f'not in {formatted_input} or "{col_name}" IS NOT NULL'
        elif is_empty_tuple:
            exclude_cond = 'IS NOT NULL'
        elif input1 == '()':
            exclude_cond = 'IS NOT NULL'
        else:
            exclude_cond = 'NOT IN'
    else:
        # exclude_cond = ' IN '
        if none_check or contains_none_or_empty:
            exclude_cond = f'in {formatted_input} or "{col_name}"is NULL' 
        elif is_empty_tuple:
            exclude_cond = 'IS NULL'
        elif input1 == '()':
            exclude_cond = 'IS  NULL'
        else:
            exclude_cond = 'IN '

    if  chart_filter_data.data_type.lower() in date_list :
        quarters = {"q1":('01','02','03'),"q2":('04','05','06'),"q3":('07','08','09'),"q4":('10','11','12')}
        if isinstance(range_k,list):
            string1 =   f" {condition} {get_formatted_date_query('clickhouse',chart_filter_data.col_name,chart_filter_data.format_type)}  between '{range_k[0]}' and '{range_k[1]}'  " 
            string2 = ''
            string3 = ''
        elif chart_filter_data.format_type.lower()=='quarter':
            months = []
            for quarter in literal_eval(d111):
                months.extend(quarters.get(quarter.lower(), ()))
            d111 = tuple(months)
            if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
                string1 =   f" {condition} STRFTIME('%m', \"{chart_filter_data.col_name}\") {exclude_cond}"
            else:
                string1 =   f" {condition} STRFTIME('%m', \"{chart_filter_data.col_name}\") {exclude_cond} {d111} " 
            string2 = ''
            string3 = ''
        else:
            string1 =   f" {condition} {get_formatted_date_query('clickhouse',chart_filter_data.col_name,chart_filter_data.format_type)} in {d111} " 
            string2 = ''
            string3 = ''

    elif  chart_filter_data.data_type.lower() == 'startswith':
        string1 =f" {condition} lower(\"{chart_filter_data.col_name}\") like lower('{range_k[0]}%')"
        string2 =  ''
        string3 =  ''
        
    elif chart_filter_data.data_type.lower() == 'endswith':
        string1 = f" {condition} lower(\"{chart_filter_data.col_name}\") like lower('%{range_k[0]}')"
        string2 = ''
        string3 =  ''
        
    elif  chart_filter_data.data_type.lower() in  integer_list  or chart_filter_data.data_type.lower() in char_list or  chart_filter_data.data_type.lower() in bool_list :
        if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
            string1 = f" {condition} \"{chart_filter_data.col_name}\" {exclude_cond}"
        else:
            string1 = f" {condition} \"{chart_filter_data.col_name}\" {exclude_cond} {d111}"
        string2 =  ''
        string3 =  ''
        
    elif chart_filter_data.data_type.lower() == 'aggregate' :
       
        string1 =   ''
        string2 = " "
        string3 = f" having {chart_filter_data.format_type}(\"{chart_filter_data.col_name}\") between {range_k[0]} and {range_k[1]}"
        
    response_data = {
        "string1":string1,
        "string2":string2,
        "string3":string3
    }
    return response_data


def date_data_change(format,data,value):
    data = literal_eval(data)
    month_map = {
                    '01': 'January',
                    '02': 'February',
                    '03': 'March',
                    '04': 'April',
                    '05': 'May',
                    '06': 'June',
                    '07': 'July',
                    '08': 'August',
                    '09': 'September',
                    '10': 'October',
                    '11': 'November',
                    '12': 'December'
                }
    if value==0:
        if format == '%m':
            month_nums= []
            
            for i in data:
                month_nums.append(list(month_map.keys())[list(month_map.values()).index(i)])
            result_data = tuple(month_nums)
        else:
            result_data = data
    else:
        if format == '%m':
            result_data = [month_map[month] if month in month_map else None for month in data] 
        else:
            result_data = data
    return str(result_data)


def drill_filteration(condition,col_name,data,is_date,date_col):
    if is_date:
        string1 =   f" {condition} {get_formatted_date_query('clickhouse',date_col,col_name)} in ('{data}') " 
        string2 = ''
        string3 = '' 
    else:
        string1 =   f" {condition} \"{col_name}\" in ('{data}') " 
        string2 = ''
        string3 = ''    
    response_data = {
        "string1":string1,
        "string2":string2,
        "string3":string3
    }
    return response_data








def Custom_joining_filter1(condition,chart_filter_data,type_of_db,drill_downs,dash_input_data,drill_is_exclude = False):
    if drill_is_exclude:
        exclude_cond = 'NOT IN'
    else:
        exclude_cond = ' IN '
    try:
        if chart_filter_data.format_type: 
            format_type = chart_filter_data.format_type
        else:
            format_type=''
        data_type = chart_filter_data.data_type.lower().replace('nullable(','').split('(')[0].replace(')','')
        input1 = chart_filter_data.filter_data
        formatted_input,contains_none_or_empty,none_check,is_empty_tuple = is_tuple_format(input1)
        col_name= chart_filter_data.col_name
        if chart_filter_data.is_exclude:
            if none_check or contains_none_or_empty:
                exclude_cond = f'in {formatted_input} or "{col_name}" IS NOT NULL'
            elif is_empty_tuple:
                exclude_cond = 'IS NOT NULL'
            elif input1 == '()':
                exclude_cond = 'IS NOT NULL'
            else:
                exclude_cond = f'NOT IN '
        else:
            if none_check or contains_none_or_empty:
                exclude_cond = f'in {formatted_input} or "{col_name}"is NULL' 
            elif is_empty_tuple:
                exclude_cond = 'IS NULL'
            elif input1 == '()':
                exclude_cond = 'IS  NULL'
            else:
                exclude_cond = 'IN '

    except:
        none_check = False  # Ensure it's always defined
        is_empty_tuple = False
        contains_none_or_empty = False
        input1 = ''
        
        if chart_filter_data.column_datatype.lower() in date_list11 :
            format_type = 'year/month/day hour:minute:seconds'
        elif chart_filter_data.column_datatype.lower() in timestamp_list:
            format_type = 'year/month/day'
        else:
            format_type=''
        data_type = chart_filter_data.column_datatype.lower()
        col_name = chart_filter_data.column_name
    if dash_input_data:
        p = dash_input_data
        top_bottom=False
    elif drill_downs:
        top_bottom = False
        col = col_name
        for item in drill_downs:
            if col in item.keys():
                keys = item[col]
                p = chart_filter_data.filter_data.replace(')',f"'{keys}')")
            else:
                p= chart_filter_data.filter_data
                
    else:
        try:
            if chart_filter_data.top_bottom:
                p=''
                top_bottom = True
                top_data = literal_eval(chart_filter_data.top_bottom)
            else:
                p = chart_filter_data.filter_data
                top_bottom=False
        except:
            p = chart_filter_data.filter_data
            top_bottom=False
    range_k = p
    d111=date_data_change(format_type,p,0)
    if  data_type in date_list :
        quarters = {"q1":('01','02','03'),"q2":('04','05','06'),"q3":('07','08','09'),"q4":('10','11','12')}
        if isinstance(range_k,list) and chart_filter_data.relative_date is not None:  #relative dates
            string1 =   f" {condition} ((\"{col_name}\" >= (datetime {range[0]})) AND (\"{col_name}\" < (datetime {range_k[1]})))" 
            string2 = ''
            string3 = ''
            string4= ''
            string5 = ''
        elif isinstance(range_k,list):
            string1 =   f" {condition} {get_formatted_date_query('clickhouse',col_name,format_type)}  between '{range_k[0]}' and '{range_k[1]}'  " 
            string2 = ''
            string3 = ''
            string4= ''
            string5 = ''
        elif top_bottom:
            string1 = '' 
            string2 = ''
            string3 = ''
            string4 = f' {top_data[1]}(\"{top_data[0]}\") {top_data[3]} ,'
            string5 = f' Limit {top_data[2]}  '
        elif format_type.lower()=='quarter':
            months = []
            for quarter in literal_eval(d111):
                months.extend(quarters.get(quarter.lower(), ()))
            d111 = tuple(months)
            if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
                string1 = f" {condition} STRFTIME('%m', \"{col_name}\") {exclude_cond}" 
            else:
                string1 =   f" {condition} STRFTIME('%m', \"{col_name}\") {exclude_cond} {d111} " 
            string2 = ''
            string3 = ''
            string4= ''
            string5 = ''
        else:
            if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
                string1 = f" {condition} {get_formatted_date_query('clickhouse',col_name,format_type)} {exclude_cond}"
            else:
                string1 =   f" {condition} {get_formatted_date_query('clickhouse',col_name,format_type)} {exclude_cond} {d111} " 
            string2 = ''
            string3 = ''
            string4= ''
            string5 = ''


    elif  data_type == 'startswith':
        string1 =f" {condition} lower(\"{col_name}\") like lower('{range_k[0]}%')"
        string2 =  ''
        string3 =  ''
        string4= ''
        string5 = ''
        
    elif data_type == 'endswith':
        string1 = f" {condition} lower(\"{col_name}\") like lower('%{range_k[0]}')"
        string2 = ''
        string3 =  ''
        string4= ''
        string5 = ''
        
    elif  data_type in  integer_list  or data_type in char_list or  data_type in bool_list :
        if top_bottom:
            string1 = f""
            string2 =  ''
            string3 =  ''
            string4 = f' {top_data[1]}(\"{top_data[0]}\") {top_data[3]} ,'
            string5 = f' Limit {top_data[2]}  '
        else:
            try:
                input1 = chart_filter_data.filter_data
                if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
                    string1 = f" {condition} \"{col_name}\" {exclude_cond}"
                else:
                    string1 = f" {condition} \"{col_name}\" {exclude_cond} {d111}"
            except:
                string1 = f" {condition} \"{col_name}\" {exclude_cond} {d111}"
                
            string2 =  ''
            string3 =  ''
            string4= ''
            string5 = ''
        
    elif data_type == 'aggregate' :
       
        string1 =   ''
        string2 = ""
        string3 = f"  {format_type}(\"{col_name}\") between {range_k[0]} and {range_k[1]} ,"
        string4= ''
        string5 = ''

    elif data_type == 'calculated':
        pattern = r'\b(avg|min|max|sum|count)\b'

        matches = re.findall(pattern, str(chart_filter_data.field_logic).lower(), re.IGNORECASE)
        if  matches:
            string1 =  ''
            string2 = ""
            string3 = f"  {format_type}({chart_filter_data.field_logic}) between {range_k[0]} and {range_k[1]} "
            string4= ''
            string5 = ''
        else:
            if none_check or is_empty_tuple or contains_none_or_empty or input1 == '()':
                string1 = f" {condition} {chart_filter_data.field_logic} {exclude_cond}"
            else:
                string1 = f" {condition} {chart_filter_data.field_logic} {exclude_cond} {d111}"
            string2 =  ''
            string3 =  ''
            string4= ''
            string5 = ''


    else:
        pass
    response_data = {
        "string1":string1,
        "string2":string2,
        "string3":string3,
        "string4":string4,
        "string5":string5
    }
    return response_data



def is_tuple_format(variable):
    try:
        parsed_var = ast.literal_eval(variable)  # Convert string to Python object

        if not isinstance(parsed_var, tuple):
            return False, False, False, False  # Not a tuple, return all False

        # Check if the tuple contains None or is empty
        contains_none_or_empty = any(item is None or item == "" for item in parsed_var)
        if contains_none_or_empty:
            input = tuple(item for item in parsed_var if item is not None and item != '')
            # contains_none_or_empty = True
        else:
            input = tuple(parsed_var)
        input = str(input).replace(',)', ')')
        none_check = any(item is None for item in input)
        is_empty_tuple = input == '()'
        if is_empty_tuple:
            contains_none_or_empty = False
        else:
            pass
        
        return input, contains_none_or_empty, none_check, is_empty_tuple

    except (SyntaxError, ValueError):
        return False, False, False, False 

def custom_date_transformation(sql_query, target_dialect):
    transpiled = transpile(sql_query, write=target_dialect)[0]

    if target_dialect == 'postgres':
        transpiled = transpiled.replace("STRFTIME('%W',", "EXTRACT(WEEK FROM")
        transpiled = transpiled.replace("STRFTIME('%w',", "EXTRACT(DOW FROM")

    elif target_dialect == 'mysql':
        transpiled = transpiled.replace("STRFTIME('%W',", "WEEK(")
        transpiled = transpiled.replace("STRFTIME('%w',", "WEEKDAY(")

    elif target_dialect == 'tsql':  # SQL Server (Microsoft SQL Server)
        transpiled = transpiled.replace("STRFTIME('%W',", "DATEPART(WEEK,")
        transpiled = transpiled.replace("STRFTIME('%w',", "DATEPART(WEEKDAY,")

    elif target_dialect == 'oracle':
        transpiled = transpiled.replace("STRFTIME('%W',", "TO_CHAR(")  # Oracle uses TO_CHAR for week
        transpiled = transpiled.replace("STRFTIME('%w',", "TO_CHAR(")

    elif target_dialect == 'snowflake':
        transpiled = transpiled.replace("STRFTIME('%W',", "EXTRACT(WEEK FROM")
        transpiled = transpiled.replace("STRFTIME('%w',", "EXTRACT(DAYOFWEEK FROM")
    elif target_dialect == 'clickhouse':
        transpiled = transpiled.replace("STRFTIME('%W',", "toWeek(")
        transpiled = transpiled.replace("STRFTIME('%w',", "toDayOfWeek(")

    elif target_dialect == 'sqlite':
        pass

    else:
        raise ValueError(f"Unsupported database type: {target_dialect}")

    return transpiled

def data_retrieve_filter(string1,string2,string3,data_sourse_string,col,row,pivot_measure,type_of_db):
    try:
        column_string1 = {"col":[],"row":[],"pivot_measure":[]}
        response_col1 = {"col":[],"row":[],"pivot_measure":[]}
        groupby_string1 = ' group by '
        groupby_string = ''
        abc= [col,row,pivot_measure]
        check = True if len(abc[0])>0 else False
        for index,col_values in enumerate(abc):
            if index == 0:
                current_value = "col"
            elif index == 1:
                current_value = "row"
            else:
                current_value = 'pivot_measure'
            query_string= []
            response_col = []
            group_string = ''
            for index1,i in enumerate(col_values):    
                c1 = i[0]   #column
                if i[1]:
                    d1 = i[1]
                else:
                    d1 = 'varchar'  #datatype
                f1 = i[2] #format
                d1  = d1.split('(')[0] 
                alias = i[3] #columnalias
                if alias:
                    column_data = user_alias_for_multi_col(c1,f1,d1,alias,index1,current_value,col_values)
                    if column_data['status'] ==200:
                        group_string+=column_data['groupby_string']
                        response_col+=column_data['response_col']
                        query_string +=column_data['query_string']
                    else:
                        return {'status':400,'message':column_data['message']}
                    
                else:
                    column_data= dev_alias_for_mult_col(c1,f1,d1,alias,index1,current_value,col_values)
                    if column_data['status'] ==200:
                        group_string+=column_data['groupby_string']
                        response_col+=column_data['response_col']
                        query_string +=column_data['query_string']
                    else:
                        return {'status':400,'message':column_data['message']}
            groupby_string += group_string
            groupby_string1 += groupby_string
            if index==0:
                column_string1['col'] = query_string
            elif index==1:
                column_string1['row'] = query_string
            else:
                column_string1['pivot_measure'] = query_string
            if index==0:
                response_col1['col'] = response_col
            elif index==1:
                response_col1['row'] = response_col
            else:
                response_col1['pivot_measure'] = response_col
        combined_values = column_string1['col'] + column_string1["row"] + column_string1['pivot_measure']
        a1_combined = ','.join(combined_values)
        if groupby_string1.lower()==' group by ':
            groupby_string1=''
        else:
            pass
        if type_of_db.lower() in ['microsoftsqlserver','oracle']:
            excluded_functions = ['sum(', 'max(', 'min(', 'count(']
            combined_values1 =[re.sub(r'\s*AS\s*.*$', '', sql_str).strip() for sql_str in combined_values if not any(func in sql_str for func in excluded_functions)]
            a1_combined1 = ','.join(combined_values1)
            
            query_string1 = data_sourse_string.replace('*',a1_combined)+ string1 + ' group by ' +a1_combined1.strip(',') + string3
        else:
            if a1_combined:
                query_string1 = data_sourse_string.replace('*',a1_combined)+ string1 + groupby_string1.strip(',') + string3
            else:
                query_string1 = data_sourse_string+ string1 + groupby_string1.strip(',') + string3
        query_string1 = custom_date_transformation(query_string1,dtype_fun(type_of_db))
        query_user = query_parsing(query_string1,'sqlite',type_of_db)
        temp1 = {
            "status" : 200,
            "column_string" :response_col1,
            "columns" : column_string1['col'],
            "rows" : column_string1['row'],
            "pivot_measures":column_string1['pivot_measure'],
            "query" : query_string1,
            "group_string" : groupby_string1.strip(','),
            "user_col":a1_combined,
            "user_query" : query_user

        }
        return temp1
    except Exception as e:
        temp = {
            "status" : 400,
            "message" : str(e)
        }
    return temp

def literal_eval(data):
    if data==None or data=="":
        data1 = data
    else:
        if isinstance(data,str):
            data1=ast.literal_eval(data)
        else:
            data1=data
    return data1


class Multicolumndata_with_filter(CreateAPIView):  
    serializer_class = GetTableInputSerializer11
    @csrf_exempt
    @transaction.atomic
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                col = serializer.validated_data['col']
                row = serializer.validated_data['row']
                query_set_id  = serializer.validated_data['queryset_id']
                datasource_querysetid = serializer.validated_data['datasource_querysetid']
                filter_id = serializer.validated_data["filter_id"]
                hierarchy_id = serializer.validated_data['hierarchy_id']
                drill_downs = serializer.validated_data['drill_down']
                next_drill_down = serializer.validated_data['next_drill_down']
                is_date = serializer.validated_data['is_date']
                hierarchy = serializer.validated_data['hierarchy']
                parent_user = serializer.validated_data['parent_user']
                page_count = serializer.validated_data['page_count']
                order_column = serializer.validated_data['order_column']
                pivot_measure = serializer.validated_data['pivot_measure']
                
                
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            if parent_user is None or parent_user =='':
                user_id = tok1['user_id']
            else:
                user_id=parent_user
            if len(col)<=0 and len(row)<=0:
                result_response = {
                'message':'sucess',
                'hierarchy':hierarchy,
                "is_date":is_date,
                "next_drill_down":next_drill_down,
                "data" :[],
                "table_data":[],
                "filter_id_list" : filter_id,
                "custom_query" : None,
                "columns"  : [] ,
                "rows" : []
                }
                return Response(result_response,status = status.HTTP_200_OK)
            else:
                pass
            
            copy_col= copy.deepcopy(col)
            copy_row=copy.deepcopy(row)
            copy_pivot_measure = copy.deepcopy(pivot_measure)
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)            
            try:         
                if datasource_querysetid is not None:
                    query_data = DataSource_querysets.objects.get( datasource_querysetid= datasource_querysetid,user_id = user_id)
                else:
                    query_data = QuerySets.objects.get(queryset_id = query_set_id,user_id = user_id)
                
            except Exception as e:
                return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)

            if query_data:
                data_sourse_string = f'select * from multi_table{user_id}' 
            else:
                return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)    
            
            string1=' where '
            string2=''
            string3=' having '
            string4 = ' order by '
            string5= ''
            group = []
            if drill_downs !=[]:
                if filter_id:
                    for index,filter in enumerate(filter_id):
                        try:
                            chart_filter_data = ChartFilters.objects.get(filter_id = filter)
                        except:
                            return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                        if chart_filter_data:
                            
                            if string1.lower() == ' where ':
                                condition = ''
                            else:
                                condition = 'and'

                            if chart_filter_data.top_bottom is not None:
                                condition=''
                            # if index==0:
                            custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3']
                            string4 += custom_one['string4']
                            string5 += custom_one['string5']
                            # else:
                            #     custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                            #     string1 += custom_one['string1']
                            #     string2 += custom_one['string2']
                            #     string3 += custom_one['string3']
                            #     string4 += custom_one['string4']
                            #     string5 += custom_one['string5']
                        
                        else:
                            pass
                else:
                    pass
                for index,drill in enumerate(drill_downs):
                    
                    for key,value in drill.items():
                        group.append(f' \"{key}\",')
                        if len(filter_id)>0:
                            if string1.lower() == ' where ':
                                custom_cond = ''
                            else:
                                custom_cond=' and '
                        else:
                            custom_cond = ''
                        if is_date:
                            date_col = col[0][0]
                            col[0][2] = next_drill_down
                        else:
                            date_col=''
                            col[0][0] = next_drill_down
                        if index==0:
                            custom_one = drill_filteration(custom_cond,key,value,is_date,date_col)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3'] 
                        else:
                            custom_one =drill_filteration('and',key,value,is_date,date_col)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3']
                
            else:
                if filter_id:
                    for index,filter in enumerate(filter_id):
                        try:
                            chart_filter_data = ChartFilters.objects.get(filter_id = filter)
                        except:
                            return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                        if chart_filter_data:
                            
                            if string1.lower() == ' where ':
                                condition = ''
                            else:
                                condition = 'and'
                            if chart_filter_data.top_bottom is not None :
                                condition=''
                            # if index==0:
                            custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3'] 
                            string4 += custom_one['string4']
                            string5 += custom_one['string5']
                            # else:
                                # custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                                # string1 += custom_one['string1']
                                # string2 += custom_one['string2']
                                # string3 += custom_one['string3']
                                # string4 += custom_one['string4']
                                # string5 += custom_one['string5']
                        else:
                            pass
                else:
                    pass
            if hierarchy !=[]:
                stringa =' where '
                stringb=''
                stringc=' having '
                stringd = ' order by '
                stringe= ''
                if filter_id:
                        drill_downs=[]
                        
                        for index,filter in enumerate(filter_id):
                            try:
                                chart_filter_data = ChartFilters.objects.get(filter_id = filter)
                            except:
                                return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                            if chart_filter_data:
                                
                                if stringa.lower() == ' where ':
                                    condition = ''
                                else:
                                    condition = 'and'

                                if chart_filter_data.top_bottom is not None  :
                                    condition=''
                                # if index==0:
                                custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                                stringa += custom_one['string1']
                                stringb += custom_one['string2']
                                stringc += custom_one['string3'] 
                                stringd += custom_one['string4']
                                stringe += custom_one['string5']
                                # else:
                                #     custom_one = Custom_joining_filter1(condition,chart_filter_data,conn_type,drill_downs,False)
                                #     stringa += custom_one['string1']
                                #     stringb += custom_one['string2']
                                #     stringc += custom_one['string3'] 
                                #     stringd += custom_one['string4']
                                #     stringe += custom_one['string5']
                            else:
                                pass
                else:
                    pass
                if stringd.lower() == ' order by ':
                    stringd=''

                if stringa.lower() == ' where ':
                    stringa=''
            
                if stringc.lower() == ' having ':
                    stringc=''
                stringd=stringd.rstrip(',')
                stringc = stringc.rstrip(',')
                stringe = stringe.rstrip(',')
                saved_query = data_retrieve_filter(stringa,stringb,stringc,data_sourse_string,copy_col,copy_row,copy_pivot_measure,conn_type)
                if order_column is None and col== []:
                    order_column = row[0]
                    order_query_string = order_column_func(order_column,conn_type)
                    if string4.lower() != '':
                        order_query_string +=f""" , {stringd.replace(' order by ','')}"""
                elif order_column is   None and col!=[]:
                    order_column = col[0]
                    order_query_string = order_column_func(order_column,conn_type)
                    if string4.lower() != '':
                        order_query_string +=f""" , {stringd.replace(' order by ','')}"""
                else:
                    order_query_string = order_column_func(order_column,conn_type)
                    if string4.lower() != '':
                        order_query_string +=f""" , {stringd.replace(' order by ','')}"""

                if saved_query['status'] ==200:
                    db_query_store  = saved_query['user_query'].replace(f'multi_table{user_id}',f'({query_data.custom_query}) temp_table')
                    db_query_store+=order_query_string
                else:
                    return Response({'message':saved_query['message']},status = status.HTTP_400_BAD_REQUEST)
                db_query_store+= stringe #Drill Down LImit added
            else:
                pass
              
            if string4.lower() == ' order by ':
                string4=''
            if string1.lower() == ' where ':
                string1=''
            
            if string3.lower() == ' having ':
                string3=''
            else:
                pass
            string4=string4.rstrip(',')
            string3 = string3.rstrip(',')
            string5 = string5.rstrip(',')
            build_query = data_retrieve_filter(string1,string2,string3,data_sourse_string,col,row,pivot_measure,conn_type)
            if  string4 != '' and order_column is None:
                order_query_string = string4
            elif (order_column is None and col== []):
                order_column = row[0]
                order_query_string = order_column_func(order_column,conn_type)
                if string4.lower() != '':
                    order_query_string +=f""" , {string4.replace(' order by ','')}"""
                    
            elif order_column is  None and col!=[] and string4 == '':
                order_column = col[0]
                order_query_string = order_column_func(order_column,conn_type)
                if string4.lower() != '':
                    order_query_string +=f""" , {string4.replace(' order by ','')}"""
            else:
                order_query_string = order_column_func(order_column,conn_type)
                if string4.lower() != '':
                    order_query_string +=f""" , {string4.replace(' order by ','')}"""
            if build_query['status'] ==200:  
                db_query_store1  = build_query['user_query'].replace(f'multi_table{user_id}',f'({query_data.custom_query}) temp_table')
                db_query_store1+=order_query_string
            else:
                return Response({'message':build_query['message']},status = status.HTTP_400_BAD_REQUEST)
            db_query_store1+=string5
            db_query_store1 = query_parsing(db_query_store1,'sqlite',conn_type.lower())
            execute_data = execution_query(db_query_store1,cur,conn_type.lower()) 
            if execute_data['status']==200:
                row_data = execute_data['results_data']
            else:
                return Response({"message":execute_data['message']},status=status.HTTP_404_NOT_FOUND)
            data = [list(row) for row in row_data]
            
            
                        
            result = format_sheet_data(build_query,data)
            table_result = format_sheet_data(build_query,data)
            cur.close()
            
            if hierarchy !=[]:
                if len(col)>0 or len(row)>0:
                    custome_query = db_query_store
                else:
                    custome_query = None
            else:
                if len(col)>0 or len(row)>0:
                    custome_query = db_query_store1
                else:
                    custome_query = None 
            result_response = {
                'message':'sucess',
                'hierarchy':hierarchy,
                "is_date":is_date,
                "next_drill_down":next_drill_down,
                "data" :result,
                "table_data":table_result,
                "filter_id_list" : filter_id,
                "custom_query" : custome_query,
                "columns"  : saved_query['column_string']['col'] if hierarchy !=[] else build_query['column_string']['col'] ,
                "rows" : saved_query['column_string']['row'] if hierarchy !=[] else build_query['column_string']['row'] ,
                "pivot_measure" :saved_query['column_string']['pivot_measure'] if hierarchy !=[] else build_query['column_string']['pivot_measure']
                }
            return Response(result_response,status = status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        


def order_column_func(order_column,database):
    column = order_column[0]
    data_type = order_column[1]
    format_type = order_column[2]
    alias = order_column[3]
    try:
        if order_column[4]:
            order = order_column[4]
        else:
            order = 'ASC'
    except:
        order = 'ASC'
    format_convert = date_format(format_type,data_type)
    if alias =="":
        if data_type.lower() in date_list  and format_type.lower() == 'month':
            order_by_string = f""" ORDER BY CASE 
                WHEN \"{format_type}({column})\" = 'January' THEN 1
                WHEN \"{format_type}({column})\" = 'February' THEN 2
                WHEN \"{format_type}({column})\" = 'March' THEN 3
                WHEN \"{format_type}({column})\" = 'April' THEN 4
                WHEN \"{format_type}({column})\" = 'May' THEN 5
                WHEN \"{format_type}({column})\" = 'June' THEN 6
                WHEN \"{format_type}({column})\" = 'July' THEN 7
                WHEN \"{format_type}({column})\" = 'August' THEN 8
                WHEN \"{format_type}({column})\" = 'September' THEN 9
                WHEN \"{format_type}({column})\" = 'October' THEN 10
                WHEN \"{format_type}({column})\" = 'November' THEN 11
                WHEN \"{format_type}({column})\" = 'December' THEN 12

                ELSE 13
                END {order} """

        elif data_type.lower() in date_list and format_type.lower() =='weekdays':
            order_by_string = f""" ORDER BY STRFTIME('{format_convert}', "{column}") {order} """
        elif format_type.lower() == 'count_distinct':
            order_by_string = f""" Order by \"CNTD({column})\" {order} """
        elif data_type.lower() == 'aggregate':
            order_by_string  = f""" order by \"{format_type}({column})\" {order}"""
        elif data_type.lower() in date_list:
            order_by_string = f' Order by \"{format_type}({column})\" {order}'
        else:
            order_by_string = f' Order by \"{column}\" {order}'
    else:
        if data_type.lower() in date_list  and format_type.lower() == 'month':
            # order_by_string = f""" ORDER BY toMonth(\"{column}\") {order} """
            order_by_string = f""" ORDER BY CASE 
                WHEN \"{alias}\" = 'January' THEN 1
                WHEN \"{alias}\" = 'February' THEN 2
                WHEN \"{alias}\" = 'March' THEN 3
                WHEN \"{alias}\" = 'April' THEN 4
                WHEN \"{alias}\" = 'May' THEN 5
                WHEN \"{alias}\" = 'June' THEN 6
                WHEN \"{alias}\" = 'July' THEN 7
                WHEN \"{alias}\" = 'August' THEN 8
                WHEN \"{alias}\" = 'September' THEN 9
                WHEN \"{alias}\" = 'October' THEN 10
                WHEN \"{alias}\" = 'November' THEN 11
                WHEN \"{alias}\" = 'December' THEN 12

                ELSE 13
                END {order} """

        elif data_type.lower() in date_list and format_type.lower() =='weekdays':
            order_by_string = f""" ORDER BY STRFTIME('{format_convert}', "{column}") {order} """
        else:
            order_by_string = f'Order by \"{alias}\" {order}'
    order_by_string = f'SELECT 1 {order_by_string} '

# Extract just the ORDER BY part
    query_string1 = custom_date_transformation(order_by_string,dtype_fun(database))

    query_user = query_parsing(query_string1,'sqlite',database)
    converted_order_by_clause = query_user.split(' ', 2)[-1]

    return f' {converted_order_by_clause}'





def format_sheet_data(build_query,result_data):
    try:
        data = {
                "col_data" : build_query['column_string'],
                "row_data" : result_data
            }
        if len(build_query['column_string']['col'])>0 or len(build_query['column_string']['row'])>0:
            columns = [col.strip() for col in data["col_data"]["col"]]
            row_labels = [row.strip() for row in data["col_data"]["row"]]
            pivot_measure = [pivot.strip() for pivot in data["col_data"]["pivot_measure"]]

            result = {
                "col": [],
                "row": [],
                "pivot_measure":[]
            }

            for index,col in enumerate(columns):
                col_index = columns[index:].index(col)
                col_index = col_index+index
                
                result["col"].append({
                    "column": col.replace('"',''),
                    "result_data": [ row[col_index] for row in data["row_data"] ]
                })
        
            for index,row_label in enumerate(row_labels):
                row_index = row_labels[index:].index(row_label)+index + len(columns) 
                result["row"].append({
                    "col": row_label.replace('"',''),
                    "result_data":  [ row[row_index] for row in data["row_data"] ]
                })
            for index,pivot in enumerate(pivot_measure):
                row_index = pivot_measure[index:].index(pivot)+index + len(columns) +len(row_labels)
                result["pivot_measure"].append({
                    "col": pivot.replace('"',''),
                    "result_data":  [ row[row_index] for row in data["row_data"] ]
                })
        else:
            result = {
                
                "col": [],
                "row": [],
                "pivot_measure":[]
            }
        return result
    except Exception as e:
        print(str(e))



class DataSource_Data_with_Filter(CreateAPIView):  
    serializer_class = GetTableInputSerializer22
    @transaction.atomic
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                datasource_queryset_id = serializer.validated_data['datasource_queryset_id']
                query_set_id  = serializer.validated_data['queryset_id']
                filter_id = serializer.validated_data["filter_id"]
                hierarchy_id = serializer.validated_data['hierarchy_id']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            user_id = tok1['user_id']
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            query_data = QuerySets.objects.get(queryset_id = query_set_id,user_id =user_id)
            if query_data:
                data_sourse_string = f'select * from data_source_table{user_id}' 
            else:
                return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)    
                                    
            
            string1 = ''
            string2 = ''
            string3 = ''
            if filter_id:
                
                query_data= QuerySets.objects.get(user_id = user_id,queryset_id = query_set_id)
                if conn_type.lower()=="microsoftsqlserver":
                    query="{}".format(query_data.custom_query)
                    cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        execute_stmt = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                    col = [column[0] for column in cur.description]
                else:
                    cursor_query_data = execution_query(query_data.custom_query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        execute_stmt = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                    col = execute_stmt.keys()
                for filter in filter_id:
                    chart_filter_data = DataSourceFilter.objects.get(filter_id = filter).col_name
                    if chart_filter_data in col:
                        pass
                    else:
                        filter_id.remove(filter)

            for index,filter in enumerate(filter_id):
                try:
                    chart_filter_data = DataSourceFilter.objects.get(filter_id = filter)
                except:
                    return Response({'message':'Data Source filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                
                if chart_filter_data:
                    
                    if index==0:
                        custom_one = Custom_joining_filter('where',chart_filter_data,conn_type)
                        string1 += custom_one['string1']
                        string2 += custom_one['string2']
                        string3 += custom_one['string3'] 
                    else:                        
                        custom_one = Custom_joining_filter('and',chart_filter_data,conn_type)
                        string1 += custom_one['string1']
                        string2 += custom_one['string2']
                        string3 += custom_one['string3']
            Final_string = data_sourse_string + string1 +string2 + string3
            db_string =query_parsing(Final_string,'sqlite',conn_type)
            user_string = db_string.replace(f'data_source_table{user_id}',f'({query_data.custom_query}) temp1')
            execute_data = execution_query(user_string,cur,conn_type)
            if execute_data['status'] ==200:
                rows = execute_data['results_data']
            else:
                return Response({'message':execute_data['message']},status =status.HTTP_404_NOT_FOUND)

            data =[]
            for i in rows:
                a = list(i)
                data.append(a)
            if datasource_queryset_id is  None:
                
                abc = DataSource_querysets.objects.create(
                queryset_id  = query_set_id,
                user_id = user_id,
                hierarchy_id = hierarchy_id,
                table_names = query_data.table_names,
                filter_id_list = filter_id,
                is_custom_sql = query_data.is_custom_sql,
                custom_query = user_string
                 )
                id = abc.pk
            else:
                abc = DataSource_querysets.objects.filter( datasource_querysetid = datasource_queryset_id ).update(
                queryset_id  = query_set_id,
                user_id = user_id,
                hierarchy_id=hierarchy_id,
                table_names = query_data.table_names,
                filter_id_list = filter_id,
                is_custom_sql = query_data.is_custom_sql,
                custom_query = user_string,
                updated_at = datetime.datetime.now()
                 )
                id = datasource_queryset_id
            final_result = {
                "filter_list":filter_id,
                "datasource_queryset_id" : id,
                "query" : user_string
                
            }
            cur.close()
            
            return Response({'message':'sucess',"data" :final_result},status = status.HTTP_200_OK)
            
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)



class alias_attachment(CreateAPIView):
    serializer_class = alias_serializer
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                tables_list = serializer.validated_data['tables_list']
                count_item = {}
                result_list = []
                for i in tables_list:
                    if i[1] in count_item:
                        count_item[i[1]] +=1
                    else:
                        count_item[i[1]] =0
                    string = f"{i[1]}{str(count_item[i[1]]).replace('0','')}"
                    result_list.append([i[0],i[1],string])
                return Response({'message':'sucess','table_names':result_list},status=status.HTTP_200_OK)
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)
        

def alias_to_joins(tables_list,dbtype):
    if tables_list == []:
        return ['*']
    else:
        count_item = {}
        result_list = []
        for i in tables_list:
            table, j = i.split('".')
            j=j.strip('"')
            table = table.strip('"')
            if j.lower() in count_item:
                count_item[j.lower()] =f'{j}({table})'
            else:
                count_item[j.lower()] =j
            if dbtype.lower()=='snowflake':
                string = f'\"{table}\".{j} as \"{count_item[j.lower()]}\"'
            else:
                string = f'{i} as \"{count_item[j.lower()]}\"'
            result_list.append(string)
        return result_list




class get_list_filters(CreateAPIView):
    serializer_class = list_filters
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                type_of_filter = serializer.validated_data['type_of_filter']
                # database_id = serializer.validated_data['database_id']
                # file_id = serializer.validated_data['file_id']
                hierarchy_id = serializer.validated_data['hierarchy_id']
                query_set_id =serializer.validated_data['query_set_id']
                user_id = tok1['user_id']
                if type_of_filter.lower() == 'datasource':
                    list_filters = DataSourceFilter.objects.filter(queryset_id = query_set_id,user_id = tok1['user_id'])
                else:
                    list_filters = ChartFilters.objects.filter(queryset_id = query_set_id,user_id = tok1['user_id'])
                if list_filters:
                    con_data =connection_data_retrieve(hierarchy_id,user_id)
                    if con_data['status'] ==200:                
                        engine=con_data['engine']
                        cur=con_data['cursor']
                        conn_type = con_data['conn']
                    else:
                        return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                    
                    query_data= QuerySets.objects.get(user_id = user_id,queryset_id = query_set_id)
                    if conn_type.lower()=="microsoftsqlserver":
                        query="{}".format(query_data.custom_query)
                        cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                        if cursor_query_data['status'] == 200:
                            execute_stmt = cursor_query_data['results_data']
                        else:
                            return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                        col = [column[0] for column in cur.description]
                    else:
                        cursor_query_data = execution_query(query_data.custom_query,cur,conn_type.lower()) 
                        if cursor_query_data['status'] == 200:
                            execute_stmt = cursor_query_data['results_data']
                        else:
                            return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                        col = execute_stmt.keys()
                    
                    filters_data = []
                    filters_data = []
                    for filter_item in list_filters:
                        if filter_item.col_name in col:
                            filters_data.append({
                                    "column_name" : filter_item.col_name,
                                    "filter_id":filter_item.filter_id,
                                })
                        else:
                            if type_of_filter.lower() == 'datasource':
                                DataSourceFilter.objects.filter(filter_id = filter_item.filter_id).delete()
                            else:
                                ChartFilters.objects.filter(filter_id = filter_item.filter_id).delete()
                    cur.close()
                    return Response({"filters_data":filters_data},status=status.HTTP_200_OK)
                else:
                    filters_data = []
                    return Response({"filters_data":filters_data},status=status.HTTP_200_OK)
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)



class Clear_Filters(CreateAPIView):
    @transaction.atomic
    def get(self,request,query_set_id,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            user_id = tok1['user_id']
            list_filters = DataSourceFilter.objects.filter(queryset_id = query_set_id,user_id = tok1['user_id'])
            if list_filters:
                DataSourceFilter.objects.filter(queryset_id = query_set_id).delete()
                DataSource_querysets.objects.filter(queryset_id = query_set_id).delete()
            else:
                pass
            return Response({'message':'Filters Cleared'},status=status.HTTP_200_OK)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)




class get_table_namesAPI(CreateAPIView):
    serializer_class = get_table_names
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                query_set_id =serializer.validated_data['query_set_id']
                hierarchy_id = serializer.validated_data['hierarchy_id']
                search = serializer.validated_data['search']
                user_id = tok1['user_id']
                con_data =connection_data_retrieve(hierarchy_id,user_id)
                if con_data['status'] ==200:                
                    engine=con_data['engine']
                    cur=con_data['cursor']
                    conn_type = con_data['conn']
                else:
                    return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
                query_data = QuerySets.objects.get(queryset_id = query_set_id,user_id = tok1['user_id'])
                list_filters = DataSourceFilter.objects.filter(queryset_id = query_set_id)
                if query_data:
                    if conn_type.lower()=="microsoftsqlserver":
                        query="{}".format(query_data.custom_query)
                        cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                        if cursor_query_data['status'] == 200:
                            data = cursor_query_data['results_data']
                        else:
                            return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                        result = cur.description
                        columns =[]
                        insertvalues = ''
                        for i in result:
                            columns.append({
                                "column":i[0],
                                "data_type" : str(i[1].__name__)
                            })  
                    else:
                        cursor_query_data = execution_query(query_data.custom_query,cur,conn_type.lower()) 
                        if cursor_query_data['status'] == 200:
                            data = cursor_query_data['results_data']
                        else:
                            return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                        result = data.cursor.description
                        columns =[]
                        insertvalues = ''
                        for i in result:
                            columns.append({
                                "column":i[0],
                                "data_type" : str(get_sqlalchemy_type(i[1]).lower().replace('nullable(','').split('(')[0].replace(')',''))

                            })  
                    filter_names = []
                    if list_filters:
                        for i in list_filters:
                            filter_names.append(i.col_name)
                    filtered_data = [item for item in columns if item['column'] not in filter_names and search.lower() in item['column'].lower()]
                cur.close()
                return Response(filtered_data,status=status.HTTP_200_OK) 
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@transaction.atomic
def filter_delete(request,filter_no,type_of_filter,token):
    role_list=roles.get_previlage_id(previlage=[previlages.delete_sheet_filters,previlages.delete_dashboard_filter])
    tok1 = roles.role_status(token,role_list)
    if tok1['status']==200:
        user_id = tok1['user_id']

        if type_of_filter.lower() != 'datasource':
            aaa = ChartFilters.objects.filter(filter_id =filter_no,user_id=user_id)
            if aaa:
                aaa.delete()
            else:
                return Response({"message":'Data not Found'},status=status.HTTP_404_NOT_FOUND)
        else:
            aaa = DataSourceFilter.objects.filter(filter_id =filter_no,user_id=user_id)
            if aaa:
                aaa.delete()
            else:
                return Response({"message":'Data not Found'},status=status.HTTP_404_NOT_FOUND)
        return_data = {
            "message" : 'Filter Removed Succesfully'
        }
        return Response(return_data,status=status.HTTP_200_OK)
    else:
        return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
    



class retrieve_datasource_data(CreateAPIView):
    serializer_class = datasource_retrieve
    @transaction.atomic
    def get(self,request,db_id,queryset_id,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            con_data =connection_data_retrieve(db_id,tok1['user_id'])
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            try:
                data = QuerySets.objects.get(queryset_id = queryset_id,user_id =tok1['user_id'])
                datasource_query = DataSourceFilter.objects.filter(queryset_id=queryset_id).values_list('filter_id',flat=True)
            except Exception as e:
                return Response({'message':"Data not Found"},status=status.HTTP_400_BAD_REQUEST)
            if DataSource_querysets.objects.filter(queryset_id = queryset_id).exists():
                datasource_id = DataSource_querysets.objects.get(queryset_id = queryset_id).datasource_querysetid
            else:
                datasource_id = None
                
            datasource_json1 = data.datasource_json
            if datasource_json1 is None:
                json_data = ''
            else:
                request_data = requests.get(datasource_json1)
            en_str=encode_string(str(queryset_id))
            query_name=str('Untitled_')+str(en_str)
            filter_id = list(datasource_query)
                

            if filter_id:
                
                query_data= QuerySets.objects.get(user_id = tok1['user_id'],queryset_id = queryset_id)
                if conn_type.lower()=="microsoftsqlserver":
                    query="{}".format(query_data.custom_query)
                    cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        execute_stmt = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                    col = [column[0] for column in cur.description]
                else:
                    cursor_query_data = execution_query(query_data.custom_query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        execute_stmt = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                    col = execute_stmt.keys()
                for filter in filter_id:
                    chart_filter_data = DataSourceFilter.objects.get(filter_id = filter).col_name
                    if chart_filter_data in col:
                        pass
                    else:
                        filter_id.remove(filter)
                        DataSourceFilter.objects.get(filter_id = filter).delete()

            result_data={
                "relation_tables":literal_eval(data.joining_conditions),
                "json_data" : request_data.json(),
                "join_type":literal_eval(data.join_type),
                "filter_list":filter_id,
                "dastasource_queryset_id":datasource_id,
                "queryset_name":data.query_name if data.query_name else query_name
            }
            return Response({"dragged_data":result_data},status=status.HTTP_200_OK)      
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)

class tables_delete_with_conditions(CreateAPIView):
    serializer_class = tables_delete
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                tables_list = serializer.validated_data['tables_list']
                conditions_list = serializer.validated_data['conditions_list']
                delete_table = serializer.validated_data['delete_table']
            else:
                return Response({'message':'Serializer error'},status=status.HTTP_400_BAD_REQUEST)
            user_id = tok1['user_id']
            filtered_a = [[condition for condition in sublist if delete_table[2] not in condition] for sublist in conditions_list]

            tables_list.remove(delete_table)
            result_data = {
                "tables_list" : tables_list,
                "conditions_list":filtered_a
            }
            return Response({"data":result_data},status=status.HTTP_200_OK)  
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)
        


class delete_conition_from_list(CreateAPIView):
    serializer_class = conditions_delete
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                conditions_list = serializer.validated_data['conditions_list']
                delete_condition = serializer.validated_data['delete_condition']
            else:
                return Response({'message':'Serializer error'},status=status.HTTP_400_BAD_REQUEST)
            for index,lists in enumerate(conditions_list):
                for index1,ml in enumerate(lists):
                    if ml==delete_condition:
                        conditions_list[index].pop(index1)
            result_data = {
                "conditions_list":conditions_list
            }
            return Response({"data":result_data},status=status.HTTP_200_OK)  
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)
        




class Rename_col_name(CreateAPIView):
    serializer_class = rename_serializer
    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.rename_dimension_sheet,previlages.rename_measure_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                database_id = serializer.validated_data['database_id']
                file_id = serializer.validated_data['file_id']
                queryset_id = serializer.validated_data['queryset_id']
                old_col_name = serializer.validated_data['old_col_name']
                new_col_name = serializer.validated_data['new_col_name']
            else:
                return Response({'message':"serializer Error"},status = status.HTTP_400_BAD_REQUEST)
            user_id = tok1['user_id']
            query_data = QuerySets.objects.get(user_id = user_id,queryset_id = queryset_id)
            datasource_queryset_data = DataSource_querysets.objects.get(user_id = user_id,queryset_id = queryset_id)
            sheet_data_id = sheet_data.objects.filter(user_id = user_id,queryset_id = queryset_id)
            dashboard_id = dashboard_data.objects.filter(user_id = user_id,queryset_id = queryset_id)
            if query_data:                      
                if f'{old_col_name}' in query_data.custom_query:           
                    updated_query = query_data.custom_query.replace(f'as {old_col_name}',f' as {new_col_name}')
                    QuerySets.objects.filter(user_id = user_id,queryset_id = queryset_id).update(custom_query = updated_query,updated_at = datetime.datetime.now())
                    if f'{old_col_name}' in datasource_queryset_data.custom_query:
                        updated_query11 = datasource_queryset_data.custom_query.replace(f'as {old_col_name}',f' as {new_col_name}')
                        DataSource_querysets.objects.filter(user_id = user_id,queryset_id = queryset_id).update(custom_query = updated_query11,updated_at = datetime.datetime.now())
                    DataSourceFilter.objects.filter(user_id = user_id,queryset_id = queryset_id,col_name = old_col_name).update(col_name = new_col_name,updated_at = datetime.datetime.now())
                    ChartFilters.objects.filter(user_id = user_id,queryset_id = queryset_id,col_name = old_col_name).update(col_name = new_col_name,updated_at = datetime.datetime.now())
                    for i in sheet_data_id:
                        data1 = sheet_data.objects.get(id =i.id)
                        request_data = requests.get(data1.datasrc)
                        json_data = request_data.json()
                        updated_json_data = str(json_data).replace(f'{old_col_name}',f'{new_col_name}')
                        upload_to_s3 = updated_s3file_data(literal_eval(updated_json_data),i.datapath)
                        if upload_to_s3['status'] !=200:
                            return Response({'message':"upload File Error"},status = status.HTTP_400_BAD_REQUEST)
                    for i in dashboard_id:
                        data1 = dashboard_data.objects.get(id =i.id)
                        request_data = requests.get(data1.datasrc)
                        json_data = request_data.json()
                        updated_json_data = str(json_data).replace(f'{old_col_name}',f'{new_col_name}')
                        upload_to_s3 = updated_s3file_data(literal_eval(updated_json_data),i.datapath)
                        if upload_to_s3['status'] !=200:
                            return Response({'message':"upload File Error"},status = status.HTTP_400_BAD_REQUEST)
                    return Response({'message':'Query Updated'},status = status.HTTP_200_OK)
                else:
                    return Response({'message':"column name not found"},status = status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message':"Data not Found"},status =status.HTTP_204_NO_CONTENT)   
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)


def updated_s3file_data(data,file_key):
    json_data = json.dumps(data, indent=4)
    file_buffer = io.BytesIO(json_data.encode('utf-8'))
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
    s3.upload_fileobj(file_buffer, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(file_key))
    result = {'status':200}
    return result

class delete_database_stmt(CreateAPIView):
    serializer_class = dashboard_ntfy_stmt
    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.delete_database])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                hierarchy_id = serializer.validated_data['hierarchy_id']
                parent_data = parent_ids.objects.get(id=hierarchy_id)
                user_id = tok1['user_id']
                try:
                    match parent_data.parameter:
                        case 'server':
                            if ServerDetails.objects.filter(id = parent_data.table_id,is_sample=True).exists():
                                return Response({'message':"Cannot Deleted Default Database"},status=status.HTTP_403_FORBIDDEN)
                            statement_name = 'Database'
                            
                            name = ServerDetails.objects.get(id = parent_data.table_id,user_id = user_id).display_name
                            query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                            sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                            dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            
                        case 'files':
                            if FileDetails.objects.filter(id = parent_data.table_id,user_id=user_id).exists():
                                
                                statement_name = 'File'
                                name = FileDetails.objects.get(id = parent_data.table_id,user_id=user_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"Files Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'quickbooks':
                            if models.TokenStoring.objects.filter(id = parent_data.table_id,user=user_id).exists():
                                statement_name = 'Quickbooks'
                                name = models.TokenStoring.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"Quickbooks Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'salesforce':
                            if models.TokenStoring.objects.filter(id = parent_data.table_id,user=user_id).exists():
                                statement_name = 'Salesforce'
                                name = models.TokenStoring.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"Salesforce Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'halops':
                            if models.HaloPs.objects.filter(id = parent_data.table_id,user_id=user_id).exists():
                                statement_name = 'HaloPs'
                                name = models.HaloPs.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"Halops Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'connectwise':
                            if models.connectwise.objects.filter(id = parent_data.table_id,user_id=user_id).exists():
                                statement_name = 'ConnectWise'
                                name = models.connectwise.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"ConnectWise Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'shopify':
                            if models.Shopify.objects.filter(id = parent_data.table_id,user_id=user_id).exists():
                                statement_name = 'Shopify'
                                name = models.Shopify.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"Shopify Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                        case 'google_sheets':
                            if models.TokenStoring.objects.filter(id = parent_data.table_id,user=user_id).exists():
                                statement_name = 'Google Sheets'
                                name = models.TokenStoring.objects.get(id = parent_data.table_id).display_name
                                query_sets_count = QuerySets.objects.filter(hierarchy_id = hierarchy_id,user_id =user_id).count()
                                sheets_count = sheet_data.objects.filter(hierarchy_id = hierarchy_id,user_id=user_id).count()
                                dashboard_count = dashboard_data.objects.filter(Q(hierarchy_id__contains=f'[{hierarchy_id}') | Q(hierarchy_id__contains=f', {hierarchy_id},') | Q(hierarchy_id__endswith=f', {hierarchy_id}]')).count()
                            else:
                                return Response({'message':"GoogleSheets Data Not Exists"},status=status.HTTP_403_FORBIDDEN)
                except:
                    return Response({'message':'Data not Found'},status = status.HTTP_400_BAD_REQUEST)
                
                if query_sets_count == 0 and sheets_count ==0 and dashboard_count ==0:
                    statement = f'Are you sure to continue to Delete {statement_name} Connection?'
                else:
                    statement = f" The {statement_name} {name} is linked to {sheets_count} charts that appear on {dashboard_count} dashboards and users have {query_sets_count} SQL Queries Using this database open.Are you sure want to continue? Deleting the database will break those objects."

                return Response({'message':statement},status = status.HTTP_200_OK)
            else:
                return Response({'message':"serializer Error"},status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)

class sheet_delete_stmt(CreateAPIView):
    serializer_class = sheet_ntfy_stmt
    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.delete_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                sheet_id = serializer.validated_data['sheet_id']
                user_id = tok1['user_id']
                try:
                    sheet = sheet_data.objects.get(id = sheet_id )
                except Exception as e:
                    return Response({'message':'Data not Found'},status = status.HTTP_400_BAD_REQUEST)
                
                if sheet.is_sample == True:
                    return Response({'message':"Cannot Deleted Sheet Related to Sample Dashboard"},status=status.HTTP_403_FORBIDDEN)
                
                sheet_name = sheet.sheet_name
                dashboard_count = dashboard_data.objects.filter(
                    Q(sheet_ids__contains=f'[{sheet_id}') | Q(sheet_ids__contains=f', {sheet_id},') | Q(sheet_ids__endswith=f', {sheet_id}]')
                ).count()                
                if dashboard_count ==0:
                    statement = f' No Dashboards are Created, Are you sure to continue?'
                else:
                    statement = f'The "{sheet_name}"  is linked to {dashboard_count} dashboard. Are you sure you want to continue?'

                return Response({'message':statement},status = status.HTTP_200_OK)
            else:
                return Response({'message':"serializer Error"},status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)
        

class query_delete_stmt(CreateAPIView):
    serializer_class = query_ntfy_stmt
    @transaction.atomic
    def post(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                queryset_id = serializer.validated_data['queryset_id']
                user_id = tok1['user_id']
                try:
                    queryset = QuerySets.objects.get(queryset_id = queryset_id )
                except Exception as e:
                    return Response({'message':'Data not Found'},status = status.HTTP_400_BAD_REQUEST)
                
                if queryset.is_sample == True:
                    return Response({'message':"Cannot Deleted Queryset Related to Sample Dashboard"},status=status.HTTP_403_FORBIDDEN)


                sheets_count = sheet_data.objects.filter(queryset_id = queryset_id,user_id=user_id).count()
                dashboard_count = dashboard_data.objects.filter(Q(queryset_id__contains=f'[{queryset_id}') | Q(queryset_id__contains=f', {queryset_id},') | Q(queryset_id__endswith=f', {queryset_id}]')).count()
                if sheets_count ==0 and dashboard_count ==0:
                    statement = f'No Dependencies on this Query, Are you sure to Continue?'
                else:
                    statement = f' The Query Name  is linked to {sheets_count} charts that appear on {dashboard_count} dashboard. Are you sure you want to continue? Deleting the Query Name will break those objects.'

                return Response({'message':statement},status = status.HTTP_200_OK)
            else:
                return Response({'message':"serializer Error"},status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_400_BAD_REQUEST)



class get_datasource(CreateAPIView):
    serializer_class = GetDataSourceFilter

    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] == 200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                type_of_filter = serializer.validated_data['type_filter']
                filter_no = serializer.validated_data['filter_id']
                search = serializer.validated_data['search']
                user_id = tok1['user_id']
            else:
                return Response({'message': 'serializer error'}, status=status.HTTP_204_NO_CONTENT)

            try:
                if type_of_filter.lower() != 'datasource':
                    aaa = ChartFilters.objects.get(filter_id=filter_no, user_id=user_id)
                    field_logic = aaa.field_logic
                    if aaa.datasource_querysetid is not None:
                        query = DataSource_querysets.objects.get(datasource_querysetid = aaa.datasource_querysetid,user_id = user_id)
                    else:
                        query = QuerySets.objects.get(queryset_id = aaa.queryset_id,user_id = user_id)
                else:
                    aaa = DataSourceFilter.objects.get(filter_id= filter_no, user_id = user_id)
                    field_logic = ''
                    query = QuerySets.objects.get(queryset_id = aaa.queryset_id,user_id = user_id)
            except ChartFilters.DoesNotExist:
                return Response({"message": "ChartFilter not found."}, status=status.HTTP_404_NOT_FOUND)
            except DataSourceFilter.DoesNotExist:
                return Response({"message": "DataSourceFilter not found."}, status=status.HTTP_404_NOT_FOUND)

            #     if parent_user is None or parent_user =='':
            #     user_id = tok1['user_id']
            # else:
            #     user_id=parent_user
            con_data =connection_data_retrieve(query.hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            try:
                if aaa.top_bottom is None:
                    top_bottom_check = True
                else:
                    top_bottom_check=False
            except:
                top_bottom_check=True
            if top_bottom_check:
                try:
                    if type_of_filter.lower() == 'datasource' :
                        table_name_for_temp = f"data_source_table{user_id}"
                        query_data = QuerySets.objects.get(queryset_id = aaa.queryset_id,user_id = user_id)
                        
                    elif(type_of_filter.lower() == 'chartfilter'and aaa.datasource_querysetid is not None):
                        table_name_for_temp = f'sheet_table{user_id}'
                        query_data = DataSource_querysets.objects.get( datasource_querysetid= aaa.datasource_querysetid,user_id = user_id)                    
                    else:
                        table_name_for_temp = f'sheet_table{user_id}'
                        query_data = QuerySets.objects.get(queryset_id = aaa.queryset_id,user_id = user_id)
                    
                except Exception as e:
                    return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)
                if query_data:
                    # if aaa.file_id is not None and aaa.file_id!='':
                    #     cursor_query_data = execution_query(query_data.custom_query,cur,dbtype.lower()) 
                    #     if cursor_query_data['status'] == 200:
                    #         result_proxy = cursor_query_data['results_data']
                    #     else:
                    #         return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                    #     result_column_values = result_proxy.cursor.description
                    #     results = result_proxy.fetchall()
                    #     temp_class = Sqlite3_temp_table(query_data.custom_query,dbtype)
                    
                    #     table_created = temp_class.create(result_column_values,results,table_name_for_temp)
                    #     if table_created['status'] ==200:
                    #         data_sourse_string = f'select * from {table_name_for_temp}'
                    #     else:
                    #         return Response({'message':table_created['message']},status=status.HTTP_400_BAD_REQUEST)
                    # else:
                    #     temp_class=None
                    data_sourse_string = f'select * from ({query_data.custom_query})temp'
                else:
                    return Response({'message':'Query Set ID is not Present'},status = status.HTTP_400_BAD_REQUEST)
                if type_of_filter.lower() == 'datasource':
                    field_logic = ''
                else:
                    field_logic = aaa.field_logic    
                        
                response = get_filter_column_data(data_sourse_string,aaa.col_name,aaa.format_type,aaa.data_type,cur,conn_type,field_logic)
                if response['status'] ==200:
                    result_data = response['results_data']
                else:
                    return Response({'message':response['message']},status = status.HTTP_400_BAD_REQUEST)
                row_d = literal_eval(result_data)
            else:
                row_d=None

            fil_d = literal_eval(aaa.filter_data)
            if search:
                result = [{'label': item, 'selected': item in fil_d} for item in row_d if str(search).lower() in item.lower()]    
            elif row_d is not None:
                result = [{'label': item, 'selected': item in fil_d} for item in row_d if not (isinstance(fil_d,list) and (item is None or item =='' ))]
            else:
                result= []
            return_data = {
                "data_type":aaa.data_type,
                'filter_id': filter_no,
                'format_type':aaa.format_type,
                "column_name": aaa.col_name,
                "data_type":aaa.data_type,
                "is_exclude":aaa.is_exclude ,
                "result":literal_eval(result),
                "field_logic":field_logic,
                "range_values":fil_d if isinstance(fil_d,list) else None,
                "top_bottom":literal_eval(aaa.top_bottom)  if type_of_filter.lower() != 'datasource' else None

            }
            return Response(return_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)




def update_query(sheet_queryse_id):
    sheet_qry = SheetFilter_querysets.objects.get(Sheetqueryset_id = sheet_queryse_id)
    if sheet_qry.datasource_querysetid is None:
        query = QuerySets.objects.get(queryset_id = sheet_qry.queryset_id).custom_query
    else:
        query = DataSource_querysets.objects.get(datasource_querysetid = sheet_qry.datasource_querysetid).custom_query
    
    cleaned_query = re.sub(r'\(\s*SELECT[\s\S]+?\)\s*temp_table', '() temp_table', sheet_qry.custom_query, flags=re.IGNORECASE)
    final_query = re.sub(r'\(\s*\)\s*temp_table', f"(\n{query}\n) temp_table", cleaned_query)
    return final_query

         

class dashboard_drill_down(CreateAPIView):  
    serializer_class = dashboard_drill_down
    @csrf_exempt
    @transaction.atomic
    def post(self, request,token = None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status !=200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            col = serializer.validated_data['col']
            row = serializer.validated_data['row']
            dashboard_id = serializer.validated_data['dashboard_id']
            id = serializer.validated_data['id']
            input_list = serializer.validated_data['input_list']
            is_exclude = serializer.validated_data['is_exclude']
            sheet_id = serializer.validated_data['sheet_id']
            hierarchy_id = serializer.validated_data['hierarchy_id']
            drill_down = serializer.validated_data['drill_down']
            next_drill_down = serializer.validated_data['next_drill_down']
            is_date = serializer.validated_data['is_date']
            hierarchy = serializer.validated_data['hierarchy']
            parent_user = serializer.validated_data['parent_user']
        else:
            return Response({'message':"serializer Error"},status = status.HTTP_400_BAD_REQUEST)
        if token==None:
            user_id = dashboard_data.objects.get(id=dashboard_id).user_id
        elif parent_user:
            user_id= user_id
        else:
            user_id = tok1['user_id']
        try:
            dashboard_filters = DashboardFilters.objects.filter(dashboard_id=dashboard_id,user_id = user_id).values('id','sheet_id_list')
        except Exception as e:
            dashboard_filters=False
        sheet = sheet_data.objects.get(id = sheet_id)
        if sheet.user_ids:
            if user_id in literal_eval(sheet.user_ids) or user_id == sheet.user_id:
                user_id = sheet.user_id
            else:
                return Response({'message':'sheet data not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            user_id = sheet.user_id
        sheet_queryset = SheetFilter_querysets.objects.get(Sheetqueryset_id = sheet.sheet_filt_id,user_id=user_id)
        main_query = update_query(sheet_queryset.Sheetqueryset_id)
        main_query = re.sub(r'SELECT[\s\S]+?FROM\s+\(', 'SELECT * FROM (',  main_query, flags=re.IGNORECASE)
        main_query = re.sub(r'GROUP BY[\s\S]+$', '', main_query, flags=re.IGNORECASE).strip()
        con_data =connection_data_retrieve(hierarchy_id,user_id)
        if con_data['status'] ==200:                
            engine=con_data['engine']
            cur=con_data['cursor']
            conn_type = con_data['conn']
        else:
            return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
        try:         
            if sheet_queryset.datasource_querysetid is not None:
                query_data = DataSource_querysets.objects.get( datasource_querysetid= sheet_queryset.datasource_querysetid,user_id = user_id)
            else:
                query_data = QuerySets.objects.get(queryset_id = sheet_queryset.queryset_id,user_id = user_id)
                
        except Exception as e:
            return Response({"messgae" : "Query ID is not Present"},status=status.HTTP_400_BAD_REQUEST)
        if main_query:
            data_sourse_string = f'select * from multi_table{user_id}'
        string1 = ''
        string2 = ''
        string3 = ''
        # string4= ''
        # string5 = ''
        save_string = ''
        group = []
        filter_id = []
        if dashboard_filters:
            for filter in dashboard_filters:
                try:
                    dash_filter_data = DashboardFilters.objects.get(id = filter['id'])
                    if dash_filter_data and sheet_id in literal_eval(dash_filter_data.sheet_id_list) and str(dash_filter_data.id) in id:
                        filter_id.append(dash_filter_data.id)
                except Exception as e:
                    return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
            index=-1
            for filter in filter_id: #dashboard_filter_ids
                index+=1
                if filter in is_exclude:
                    drill_is_exclude = True
                else:
                    drill_is_exclude = False
                try:
                    dash_filter_data = DashboardFilters.objects.get(id = filter)
                    sheet_filter_data = sheet_data.objects.get(id = sheet_id ).filter_ids
                    sheet_count =0
                    top_bottom=False
                    for i in literal_eval(sheet_filter_data):
                        chart_data = ChartFilters.objects.get(filter_id = i)
                        if chart_data.top_bottom:
                            top_bottom =True
                        else:
                            sheet_count+=1

                except:
                    return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                

                if dash_filter_data:
                    input_data = input_list[id.index(str(dash_filter_data.id))]
                    if input_data==[]:
                        pass
                    else:
                        if top_bottom and sheet_count==0:
                            index= 0 if index==0 else index-1
                            custom_cond = 'where'
                        elif sheet_count>0:
                            custom_cond='and'
                        elif sheet_count>0 and top_bottom:
                            custom_cond = 'and'
                        else:
                            custom_cond = 'where'
                        if index<=0:
                            custom_one = Custom_joining_filter1(custom_cond,dash_filter_data,conn_type,drill_down,tuple(input_data),drill_is_exclude)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3']
                        else:
                            custom_one = Custom_joining_filter1('and',dash_filter_data,conn_type,drill_down,tuple(input_data),drill_is_exclude)
                            string1 += custom_one['string1']
                            string2 += custom_one['string2']
                            string3 += custom_one['string3']
                else:
                    pass
            else:
                pass
        
        for index,drill in enumerate(drill_down):
            
            for key,value in drill.items():
                group.append(f' \"{key}\",')
                if len(filter_id)>0:
                    if string1.lower() == '':
                        custom_cond = ' where '
                    else:
                        custom_cond=' and '
                else:
                    custom_cond = ' where '
                if is_date:
                    date_col = col[0][0]
                    col[0][2] = next_drill_down
                else:
                    date_col=''
                    col[0][0] = next_drill_down
                if index==0:
                    custom_one = drill_filteration(custom_cond,key,value,is_date,date_col)
                    string1 += custom_one['string1']
                    string2 += custom_one['string2']
                    string3 += custom_one['string3'] 
                else:
                    custom_one = drill_filteration('and',key,value,is_date,date_col)
                    string1 += custom_one['string1']
                    string2 += custom_one['string2']
                    string3 += custom_one['string3']   
         
        build_query = data_retrieve_filter(string1,string2,string3,data_sourse_string,col,row,[],conn_type)
        if build_query["status"] ==200:
            final_query = build_query['query']

        else:
                return Response({'message':build_query["message"]},status = status.HTTP_400_BAD_REQUEST)
        db_query_store  = build_query['user_query'].replace(f'multi_table{user_id}',f'({query_data.custom_query}) temp_table')            
        query_result = execution_query(db_query_store,cur,conn_type.lower())
        if query_result['status'] ==200:
            row_data = query_result['results_data']
        else:
            return Response({'message':query_result['message']},status = status.HTTP_400_BAD_REQUEST)
        
        data = [list(row) for row in row_data]
        cur.close()
        result = format_sheet_data(build_query,data)

        return Response({'hierarchy':hierarchy,"is_date":is_date,"next_drill_down":next_drill_down,"data" :result},status = status.HTTP_200_OK)
            



def user_alias_for_multi_col(c1,f1,d1,alias,index1,current_value,col_values):
    query_string= []
    response_col = []
    groupby_string=''
    if d1.lower() in integer_list   or d1.lower() in char_list :
        if index1 == 0 and current_value =='col':
            if f1.lower()=='count_distinct':
                query_string.append(f" count(Distinct \"{c1}\") AS \"{alias}\"")
                response_col.append(f" \"{alias}\"")
            else:
                query_string.append(f" \"{c1}\" AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
                groupby_string += f" \"{alias}\","
        else:
            if f1.lower()=='count_distinct':
                query_string.append(f" count(Distinct \"{c1}\") AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
            else:
                query_string.append(f" \"{c1}\" AS  \"{alias}\"")
                response_col.append(f" \"{alias}\"")
                groupby_string += f" \"{alias}\","
    elif  d1.lower() in bool_list:
        if index1 == 0 and current_value =='col':
            if f1.lower()=='count_distinct':
                query_string.append(f" count(distinct CASE when \"{c1}\" THEN 'True' ELSE 'False' END) AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
            else:
                query_string.append(f" CASE when \"{c1}\" THEN 'True' ELSE 'False' END AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
                groupby_string += f" \"{alias}\","
                
        else:
            if f1.lower()=='count_distinct':
                query_string.append(f" count(distinct CASE when \"{c1}\" THEN 'True' ELSE 'False' END) AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
            else:
                query_string.append(f" CASE when \"{c1}\" THEN 'True' ELSE 'False' END AS \"{alias}\" ")
                response_col.append(f" \"{alias}\"")
                groupby_string += f" \"{alias}\","
    elif d1.lower() in date_list and len(col_values)!=0:
        date_group= date_format(f1,'sqlite')

        if index1 == 0 and current_value =='col':
            if f1.lower() == 'count_distinct':
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{alias}\"" )
                response_col.append(f" \"{alias}\"" )
            else:
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{alias}\"" )
                response_col.append(f"\"{alias}\"" )
                if date_group =='%w':
                    groupby_string+=f""" STRFTIME('%w',\"{c1}\"),"""
                else:
                    groupby_string += f"\"{alias}\","
        else:

            if f1.lower() == 'count_distinct':
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{alias}\"" )
                response_col.append(f" \"{alias}\"" )
            else:
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{alias}\"" )
                response_col.append(f"\"{alias}\"" )
 
                if date_group =='%w':
                    groupby_string+=f""" STRFTIME('%w',\"{c1}\"),"""
                else:
                    groupby_string += f"\"{alias}\","  

    elif 'aggregate' == d1.lower():
        if f1.lower()=='count_distinct':
            query_string.append(f' Count(Distinct \"{c1}\") AS \"{alias}\"')
            response_col.append(f" \"{alias}\"" )
        else:
            query_string.append(f' {f1}(\"{c1}\") AS \"{alias}\"')
            response_col.append(f"\"{alias}\"" )
    elif 'calculated' == d1.lower():
        pattern = r'\b(avg|min|max|sum|count)\b'
        matches = re.findall(pattern, str(c1).lower(), re.IGNORECASE)
        if  matches:
            query_string.append(f'{f1}({c1}) as \"{alias}\"')
            response_col.append(f" \"{alias}\"" )
            
        else:
            query_string.append(f'{f1}({c1}) as \"{alias}\"')
            response_col.append(f" \"{alias}\"" )
            groupby_string += f'\"{alias}\",'
    else:
        temp11 = {"status":400,'message':'  inputs Errors'}
        return temp11
    return {'status':200,'response_col':response_col,"query_string":query_string,'groupby_string':groupby_string}



def dev_alias_for_mult_col(c1,f1,d1,alias,index1,current_value,col_values):
    query_string= []
    response_col = []
    groupby_string=''
    if d1.lower() in integer_list   or d1.lower() in char_list :
        if index1 == 0 and current_value =='col':
            if f1.lower()=='count_distinct':
                query_string.append(f" count(Distinct \"{c1}\") AS \"CNTD({c1})\"")
                response_col.append(f" \"CNTD({c1})\"")
            else:
                query_string.append(f" \"{c1}\" AS \"{c1}\" ")
                response_col.append(f" \"{c1}\"")
                groupby_string += f" \"{c1}\","
        else:
            if f1.lower()=='count_distinct':
                query_string.append(f" count(Distinct \"{c1}\") AS \"CNTD({c1})\" ")
                response_col.append(f" \"CNTD({c1})\"")
            else:
                query_string.append(f" \"{c1}\" AS  \"{c1}\"")
                response_col.append(f" \"{c1}\"")
                groupby_string += f" \"{c1}\","
    elif  d1.lower() in bool_list:
        if index1 == 0 and current_value =='col':
            if f1.lower()=='count_distinct':
                query_string.append(f" count(distinct CASE when \"{c1}\" THEN 'True' ELSE 'False' END) AS \"CNTD({c1}:OK)\" ")
                response_col.append(f" \"CNTD({c1})\"")
            else:
                query_string.append(f" CASE when \"{c1}\" THEN 'True' ELSE 'False' END AS \"{c1}\" ")
                response_col.append(f" \"{c1}\"")
                groupby_string += f" \"{c1}\","
        else:
            if f1.lower()=='count_distinct':
                query_string.append(f" count(distinct CASE when \"{c1}\" THEN 'True' ELSE 'False' END) AS \"CNTD({c1})\" ")
                response_col.append(f" \"CNTD({c1})\"")
            else:
                query_string.append(f" CASE when \"{c1}\" THEN 'True' ELSE 'False' END AS \"{c1}\" ")
                response_col.append(f" \"{c1}\"")
                groupby_string += f" \"{c1}\","
    elif d1.lower() in date_list and len(col_values)!=0:
        date_group= date_format(f1,'sqlite')
        if index1 == 0 and current_value =='col':
            if f1.lower() == 'count_distinct':
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"CNTD({c1}:OK)\"" )
                response_col.append(f" \"CNTD({c1})\"" )
            else:
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{f1}({c1})\"" )
                response_col.append(f"\"{f1}({c1})\"" )
                if date_group =='%w':
                    groupby_string+=f""" STRFTIME('%w',\"{c1}\"),"""
                else:
                    groupby_string += f"\"{f1}({c1})\","
        else:
            if f1.lower() == 'count_distinct':
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"CNTD({c1})\"" )
                response_col.append(f" \"CNTD({c1})\"" )
                groupby_string += f" \"CNTD({c1})\","
            else:
                query_string.append(f"{get_formatted_date_query('clickhouse',c1,f1)} AS \"{f1}({c1})\"" )
                response_col.append(f"\"{f1}({c1})\"" )
                if date_group =='%w':
                    groupby_string+=f""" STRFTIME('%w',\"{c1}\"),"""
                else:
                    groupby_string += f"\"{f1}({c1})\","

    elif 'aggregate' == d1.lower():
        if f1.lower()=='count_distinct':
            query_string.append(f' Count(Distinct \"{c1}\") AS \"CNTD({c1})\"')
            response_col.append(f" \"CNTD({c1})\"" )
        else:
            query_string.append(f' {f1}(\"{c1}\") AS \"{f1}({c1})\"')
            response_col.append(f"\"{f1}({c1})\"" )
    elif 'calculated' == d1.lower():
        pattern = r'\b(avg|min|max|sum)\b'

        matches = re.findall(pattern, str(c1).lower(), re.IGNORECASE)
        if  matches:
            query_string.append(f'{f1}({c1}) as \"{alias}\"')
            groupby_string += f'\"{alias}\"'
        else:
            query_string.append(f'{f1}({c1}) as \"{alias}\"')
    else:
        temp11 = {"status":400,'message':'  inputs Errors'}
        return temp11
    return {'status':200,'response_col':response_col,"query_string":query_string,'groupby_string':groupby_string}




            
     

#### search and table for sheet 
class data_table_chart(CreateAPIView):  
    serializer_class = sheet_table_serializer
    @csrf_exempt
    @transaction.atomic
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                hierarchy_id = serializer.validated_data['hierarchy_id']
                parent_user = serializer.validated_data['parent_user']
                page_no = serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                search= serializer.validated_data['search']
                sheetqueryset_id  = serializer.validated_data['sheetqueryset_id']
                queryset_id = serializer.validated_data['queryset_id']
                custom_query = serializer.validated_data['custom_query']
                columns = serializer.validated_data['columns']
                rows= serializer.validated_data['rows']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            if parent_user is None or parent_user =='':
                user_id = tok1['user_id']
            else:
                user_id=parent_user
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)    
            result = {
                
                "col": [],
                "row": []
            }
            if custom_query:
                if conn_type.lower()=="microsoftsqlserver":
                    query="{}".format(custom_query)
                    cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        result_proxy = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                else:
                    cursor_query_data = execution_query(custom_query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        result_proxy = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                row_data = result_proxy.fetchall()
                
                if search !='' or search != None:
                    data = [list(row) for row in row_data if any(search.lower() in str(cell).lower() for cell in row)]
                else:
                    data = [list(row) for row in row_data]
                result_data = pagination(request,data,page_no,page_count)
                if result_data['status'] ==200:
                    data = result_data['data']
                    total_pages = result_data['total_pages']
                    items_per_page = result_data['items_per_page']
                    total_items = result_data['total_items']
                else:
                    return Response({'message':result_data['message']},status = status.HTTP_404_NOT_FOUND) 
                response_col1 = {"col":columns,"row":rows,"pivot_measure":[]}
                build_query = {
                    "column_string" :response_col1
                }    
                result = format_sheet_data(build_query,data)
                
                cur.close()
                result_response = {
                    'message':'sucess',
                    "data" :result,
                    "total_pages":total_pages,
                    "items_per_page":items_per_page,
                    "total_items":total_items,
                    }
            else:
                result_response = {
                    'message':'sucess',
                    "data" :result,
                    "total_pages":0,
                    "items_per_page":0,
                    "total_items":0,
                    }
            return Response(result_response,status = status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        

        


# # #### search and table for  dashboard
class dashboard_table_chart(CreateAPIView):  
    serializer_class = dashboard_table_serializer
    @csrf_exempt
    @transaction.atomic
    def post(self, request,token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status ==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                hierarchy_id = serializer.validated_data['hierarchy_id']
                parent_user = serializer.validated_data['parent_user']
                page_no = serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                search= serializer.validated_data['search']
                sheet_id = serializer.validated_data['sheet_id']
                dashboard_id = serializer.validated_data['dashboard_id']
                id = serializer.validated_data['id']
                input_list = serializer.validated_data['input_list']
                is_exclude = serializer.validated_data['is_exclude']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            if token==None:
                user_id = dashboard_data.objects.get(id=dashboard_id).user_id
            elif parent_user:
                user_id= user_id
            else:
                user_id = tok1['user_id']
            if sheet_id:
                sheet_obj = sheet_data.objects.get(id = sheet_id)
                if sheet_obj.user_ids:
                    if user_id in literal_eval(sheet_obj.user_ids) or user_id == sheet_obj.user_id:
                        user_id = sheet_obj.user_id
                    else:
                        return Response({'message':'sheet data not found'},status=status.HTTP_404_NOT_FOUND)
                else:
                    user_id = sheet_obj.user_id
                sheetquery_data = SheetFilter_querysets.objects.get(Sheetqueryset_id=sheet_obj.sheet_filt_id)
                columns = literal_eval(sheetquery_data.columns)
                rows = literal_eval(sheetquery_data.rows)
                custom_query = sheetquery_data.custom_query
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            query_data1 = QuerySets.objects.get(queryset_id = sheet_obj.queryset_id,user_id = user_id) 
            try:
                dashboard_filters = DashboardFilters.objects.filter(dashboard_id=dashboard_id,user_id = user_id).values('id','sheet_id_list')
            except Exception as e:
                dashboard_filters=False
            filter_id = []
            drill_down=[]
            string1=''
            string2=''
            string3=''
            if dashboard_filters:
                for filter in dashboard_filters:
                    try:
                        dash_filter_data = DashboardFilters.objects.get(id = filter['id'])
                        if dash_filter_data and sheet_id in literal_eval(dash_filter_data.sheet_id_list) and str(dash_filter_data.id) in id:
                            filter_id.append(dash_filter_data.id)
                    except Exception as e:
                        return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                index=-1
                for filter in filter_id: #dashboard_filter_ids\
                    if filter in is_exclude:
                        is_table_exclude = True
                    else:
                        is_table_exclude = False
                    index+=1
                    try:
                        dash_filter_data = DashboardFilters.objects.get(id = filter)
                        sheet_filter_data = sheet_data.objects.get(id = sheet_id ).filter_ids
                        sheet_count =0
                        top_bottom=False
                        for i in literal_eval(sheet_filter_data):
                            chart_data = ChartFilters.objects.get(filter_id = i)
                            if chart_data.top_bottom:
                                top_bottom =True
                            else:
                                sheet_count+=1

                    except:
                        return Response({'message':'chart filter id not present in database'},status=status.HTTP_404_NOT_FOUND)
                    

                    if dash_filter_data:
                        input_data = input_list[id.index(str(dash_filter_data.id))]
                        if input_data==[]:
                            pass
                        else:
                            if top_bottom and sheet_count==0:
                                index= 0 if index==0 else index-1
                                custom_cond = 'where'
                            elif sheet_count>0:
                                custom_cond='and'
                            elif sheet_count>0 and top_bottom:
                                custom_cond = 'and'
                            else:
                                custom_cond = 'where'
                            if index<=0:
                                custom_one = Custom_joining_filter1(custom_cond,dash_filter_data,conn_type,drill_down,tuple(input_data),is_table_exclude)
                                string1 += custom_one['string1']
                                string2 += custom_one['string2']
                                string3 += custom_one['string3']
                            else:
                                custom_one = Custom_joining_filter1('and',dash_filter_data,conn_type,drill_down,tuple(input_data),is_table_exclude)
                                string1 += custom_one['string1']
                                string2 += custom_one['string2']
                                string3 += custom_one['string3']
                    else:
                        pass
                else:
                    pass
                if "group by" in custom_query.lower():
                    parts = re.split(r'(?i)group by', custom_query)
                    custom_query = parts[0]+string1+string2+string3+ 'group by ' + parts[1]
                else:
                    custom_query = custom_query +string1+string2+string3
                custom_query = query_parsing(custom_query,'sqlite',conn_type.lower())
            else:
                pass   
            if custom_query:
                if conn_type.lower()=="microsoftsqlserver":
                    query="{}".format(custom_query)
                    cursor_query_data = execution_query(query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        result_proxy = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                else:
                    cursor_query_data = execution_query(custom_query,cur,conn_type.lower()) 
                    if cursor_query_data['status'] == 200:
                        result_proxy = cursor_query_data['results_data']
                    else:
                        return Response({"message":cursor_query_data['message']},status=status.HTTP_404_NOT_FOUND)
                row_data = result_proxy.fetchall()
            else:
                row_data =[]
            if search !='' or search != None:
                data = [list(row) for row in row_data if any(search.lower() in str(cell).lower() for cell in row)]
            else:
                data = [list(row) for row in row_data]
            result_data = pagination(request,data,page_no,page_count)
            if result_data['status'] ==200:
                data = result_data['data']
                total_pages = result_data['total_pages']
                items_per_page = result_data['items_per_page']
                total_items = result_data['total_items']
            else:
                return Response({'message':result_data['message']},status = status.HTTP_404_NOT_FOUND) 
            response_col1 = {"col":columns,"row":rows}
            build_query = {
                "column_string" :response_col1
            }    
            result = format_sheet_data_for_dashboard(build_query,data)
            cur.close()
            result_response = {
                'message':'sucess',
                "data" :result,
                "total_pages":total_pages,
                "items_per_page":items_per_page,
                "total_items":total_items,
                "chartID":1,

                }
            return Response(result_response,status = status.HTTP_200_OK)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        


def format_sheet_data_for_dashboard(build_query,result_data):
    try:
        data = {
                "col_data" : build_query['column_string'],
                "row_data" : result_data
            }
        if len(build_query['column_string']['col'])>0 or len(build_query['column_string']['row'])>0:
            columns = [col.strip() for col in data["col_data"]["col"]]
            row_labels = [row.strip() for row in data["col_data"]["row"]]

            result = {
                "columns": [],
                "rows": []
            }

            for index,col in enumerate(columns):
                col_index = columns[index:].index(col)
                col_index = col_index+index
                
                result["columns"].append({
                    "column": col.replace('"',''),
                    "result": [round(float(row[col_index]),2) if type(row[col_index]) is float else row[col_index] for row in data["row_data"] ]
                })
        
            for index,row_label in enumerate(row_labels):
                row_index = row_labels[index:].index(row_label)+index + len(columns) 
                result["rows"].append({
                    "column": row_label.replace('"',''),
                    "result":  [round(row[row_index],2) if type(row[row_index])is float else row[row_index] for row in data["row_data"] ]
                })
        else:
            result = {
                
                "columns": [],
                "rows": []
            }
        return result
    except Exception as e:
        print(str(e))
