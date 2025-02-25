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
import calendar
import ast
import re
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Float, Date, Time, DateTime, Numeric,TIMESTAMP,VARCHAR,BIGINT,SMALLINT,CHAR,Text,TEXT,VARBINARY
from .views import test_token
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
from .Filters import connection_data_retrieve,server_details_check,alias_to_joins,query_parsing,delete_tables_sqlite,execution_query
created_at=datetime.datetime.now(utc),
updated_at=datetime.datetime.now(utc)


integer_list=['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double','int64','int32','float64','float32','nullable(int64)', 'nullable(int32)', 'nullable(uint8)', 
    'nullable(float(64))','int8','int16','int32','int64','float32','float16','float64','decimal(38,10)','decimal(12,2)','uuid','nullable(int8)','nullable(int16)','nullable(int32)','nullable(int64)','nullable(float32)','nullable(float16)','nullable(float64)','nullable(decimal(38,10)','nullable(decimal(12,2)']

from itertools import combinations

def relation1(tables, table_col, dbtype, join_conditions, new_joining_cond):
    try:
        # Organize table columns into dictionaries
        list_of_tables = {table: [] for table in tables}
        for table, col_name, col_type in table_col:
            if table in list_of_tables:
                list_of_tables[table].append(f'{col_name}:{col_type}')

        relation_tables = []
        comp = set(range(1, len(tables)))
        # Precompute table split names for efficiency
        table_splits = {table: table.split(' "') for table in tables}

        for table1, table2 in combinations(tables, 2):
            i, j = tables.index(table1), tables.index(table2)

            # Skip if table pair already processed
            if j not in comp:
                continue
            # data_type = data_type.lower().replace('nullable(','')
            # data_type = data_type.split('(')[0].replace(')','')
            # Build dictionaries for quick lookup
            dict1 = {col.split(':')[0]:str(col.split(':')[1]).lower().replace('nullable(','').split('(')[0].replace(')','') for col in list_of_tables[table1]}
            dict2 = { col.split(':')[0]:str(col.split(':')[1]).lower().replace('nullable(','').split('(')[0].replace(')','') for col in list_of_tables[table2]}

            # Find common keys efficiently using set intersection
            intersection_keys = dict(set(dict1.items()) & set(dict2.items()))
            if intersection_keys:
                final_data = [f'{key}:{dict1[key]}' for key in intersection_keys.keys()] + [f'{key}:{dict1[key]}' for key in intersection_keys.keys()]
                relation_tables.append((table1, table2))

                if j in comp:
                    comp.remove(j)

                    # Sort columns based on data type
                    sorted_columns = sorted(final_data, key=lambda x: x.split(':')[1].lower() not in integer_list)
                    sorted_keys = [col.split(':')[0] for col in sorted_columns]
                    # Prepare table references
                    formast, formaet = table_splits[table1][1], table_splits[table2][1]

                    # Format join condition
                    if dbtype.lower() == 'snowflake':
                        join_condition = f'{formast}.{sorted_keys[0]} = {formaet}.{sorted_keys[0]}'
                    else:
                        join_condition = f'"{formast}."{sorted_keys[0]}" = "{formaet}."{sorted_keys[0]}"'

                    # Parse query for compatibility with target DB type
                    join_condition = query_parsing(join_condition, 'sqlite', dbtype)
                    # Update conditions and new joining structure
                    if not join_conditions[j - 1]:
                        new_joining_cond[j - 1].append({
                            "table1": formast.replace('"', ''),
                            "firstcolumn": sorted_keys[0].replace('"', ''),
                            "operator": '=',
                            "secondcolumn": sorted_keys[0].replace('"', ''),
                            "table2": formaet.replace('"', '')
                        })
                        join_conditions[j - 1].append(join_condition)

        response_data = {
            "status": 200,
            "relation": relation_tables,
            "conditions": join_conditions,
            "comp": list(comp),
            "new_joining_format": new_joining_cond
        }
    except Exception as e:
        response_data = {
            "status": 404,
            "message": str(e)
        }

    return response_data


class rdbmsjoins_new(CreateAPIView):
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
                new_join_table_conditions= serializer.validated_data['joining_conditions']
                dragged_array = serializer.validated_data['dragged_array']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT) 
            # conn_setup = connection_setup(mapping_id)
            con_data =connection_data_retrieve(hierarchy_id,user_id)
            if con_data['status'] ==200:                
                engine=con_data['engine']
                cur=con_data['cursor']
                conn_type = con_data['conn']
            else:
                return Response({'message':con_data['message']},status = status.HTTP_404_NOT_FOUND)
            # serdt=server_details_check(ServerType1,server_details,file_type,file_data,joining_tables,False)
            # if serdt['status']==200:
            #     engine=serdt['engine']
            #     cur=serdt['cursor']
            # else:
            #     return Response({'message':serdt['message']},status=serdt['status'])
            
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
                # for index,i in enumerate(new_join_table_conditions):
                #     for index1,j in enumerate(i):
                #         if j:
                #             new_cond = query_parsing(j,'sqlite',dbtype)
                #             join_table_conditions[index][index1] = new_cond
                #         else:
                #             pass
                # if file_id is not None and file_id !='':
                #     for i in joining_tables:
                #         i[0] ='main'
                join_table_conditions = []
                for list1 in new_join_table_conditions:
                    make_con_list=[]
                    for conditions in list1:
                        make_con_list.append(f"""\"{conditions['table1']}\".\"{conditions['firstcolumn']}\" {conditions['operator']} \"{conditions['table2']}\".\"{conditions['secondcolumn']}\"""")
                    join_table_conditions.append(make_con_list)

                responce = building_query1(self,joining_tables,join_table_conditions,join_type,engine,conn_type,new_join_table_conditions)
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
                    converted_query1= converted_query+ f' limit 1 '
                    try:
                        if conn_type.lower() =='microsoftsqlserver':
                            result_proxy = cur.execute(converted_query1)
                        else:
                            result_proxy = cur.execute(text(converted_query1))
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
                            joining_conditions  =responce['new_joining_format'],
                            custom_query = converted_query,
                            datasource_path = file_path['file_key'],
                            datasource_json = file_path['file_url'],
                            created_at=datetime.datetime.now(utc),
                            updated_at=datetime.datetime.now(utc)
                            
                        )
                        id = a.queryset_id
                        # QuerySets.objects.filter(queryset_id=a.queryset_id).update(created_at=created_at,updated_at=updated_at)
                    else:
                        a = QuerySets.objects.filter(queryset_id = query_set_id).update(
                            user_id = user_id,
                            hierarchy_id = hierarchy_id,
                            table_names =joining_tables,
                            join_type = responce['join_types'],
                            joining_conditions  =responce['new_joining_format'],
                            custom_query = converted_query,
                            datasource_path = file_path['file_key'],
                            datasource_json = file_path['file_url'],
                            updated_at=datetime.datetime.now(utc)
                            
                        )
                        id = query_set_id
                        QuerySets.objects.filter(queryset_id=query_set_id).update(updated_at=updated_at)
                    Response_data= {
                        "hierarchy_id":hierarchy_id,
                        "query_set_id" : id,
                        'joining_condition': responce['new_joining_format'],
                        'tables_col' :responce['tables'],
                        "join_types": responce['join_types']
                        # "joining_condition_list" : joining_condition_list
                                }
                except Exception as e:
                    return Response({"message":f'{e}'},status=status.HTTP_400_BAD_REQUEST)
            
            cur.close()
            return JsonResponse({"message":"Joining tables successfully","table_columns_and_rows":Response_data},status=status.HTTP_200_OK,safe=False)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        

def building_query1(self,tables,join_conditions,join_types,engine,dbtype,new_joining_cond):
    table_col= []
    tables_a= []
    table_json = []
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
                # pyodbc cursor get column names
                # columns = cursor.columns(table=table_name)

                # columns = [{'name':column.COLUMN_NAME,'col':str(column.DATA_TYPE)} for column in columns]
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
            
            if dbtype.lower()=='snowflake':
                a =r'{}.{} "{}"'.format(schema,table_name,alias)
                tables_a.append(a)
            else:
                a =r'"{}"."{}" "{}"'.format(schema,table_name,alias)
                tables_a.append(a)
            for column in columns:
                
                alias_columns.append(f"\"{alias}\".\"{column['name']}\"")
                json_str = {"table":a,"col":column['name'],"dtype":column['col'].lower()}
                table_json.append(json_str)
                table_col.append((f'{a}',column['name'],column['col'].lower()))
    except Exception as e:
        return_data = {
            "status":400,
            "message" : f'{e}  table not present in databse'
        }
        return return_data
    tables = tables_a
    try:
        query = f"SELECT * FROM {tables[0]}"
        join_types1 = []
        # Verify join conditions match the number of joins required
        if len(tables) - 1 == sum(1 for cond in join_conditions if len(cond) > 0):
            for i in range(1, len(tables)):
                join_type = join_types[i - 1] if i - 1 < len(join_types) else 'inner'
                join_types1.append(join_type)
                query += f" {join_type} JOIN {tables[i]}"

                # Process join conditions
                for index, user_cond in enumerate(join_conditions[i - 1]):
                    if dbtype.lower() == 'snowflake':
                        user_cond = process_snowflake_condition(user_cond)
                        join_conditions[i - 1][index] = user_cond

                    query += f" {'ON' if index == 0 else 'AND'} {user_cond}"

        else:
            # Handle case where join conditions don't align with table joins
            get_data = relation1(tables, table_col, dbtype, join_conditions, new_joining_cond)
            if get_data['status'] != 200:
                return {'status':400,"message": get_data['message']}
            # Process relationship data
            comp = get_data['comp']
            relation_tables = get_data['relation']
            dynamic_cond = get_data['conditions']
            new_joining_cond_1 = get_data['new_joining_format']
            no_relation_tables = []

            for i in (comp or []):
                if not join_conditions[i - 1]:
                    no_relation_tables.append(tables[i].split(' ')[-1])
                else:
                    process_conditions(tables, join_conditions, relation_tables, i)

            if no_relation_tables:
                return {
                    "status": 204,
                    "relation": new_joining_cond_1,
                    "no_relation": no_relation_tables,
                }

            # Build the final query
            condition = build_condition_map(relation_tables, join_conditions, dynamic_cond, new_joining_cond, new_joining_cond_1)
            query = finalize_query(tables, condition, join_types, join_types1)

        return {
            "status": 200,
            "query_data": query,
            "joining": join_conditions,
            "tables": table_json,
            "join_types": join_types1,
            "make_columns": alias_columns,
            "new_joining_format": new_joining_cond,
        }

    except Exception as e:
        return {
            "status": 400,
            "message": str(e),
        }


def process_snowflake_condition(user_cond):
    """Process Snowflake-specific conditions."""
    pattern = r"(>=|<=|>|<|=)"
    parts = re.split(pattern, user_cond)
    cond1, cond2 = parts[0], parts[2]
    cond1 = '.'.join(cond1.split('.')).replace('"', '')
    cond2 = '.'.join(cond2.split('.')).replace('"', '')
    return f"{cond1} = {cond2}"


def process_conditions(tables, join_conditions, relation_tables, index):
    """Process join conditions for relationships."""
    for user_cond in join_conditions[index - 1]:
        if user_cond:
            k = find_table_relationship(tables, user_cond)
            if k:
                relation_tables.insert(index - 1, k)


def find_table_relationship(tables, condition):
    """Find table relationships based on condition."""
    pattern = r"(>=|<=|>|<|=)"
    parts = re.split(pattern, condition)
    one, three = parts[0].split('.')[0], parts[2].split('.')[0]
    return next(((t1, t2) for t1 in tables for t2 in tables if one in t1 and three in t2), None)


def build_condition_map(my_relation_tables, join_conditions, dynamic_cond, new_joining_cond, new_joining_cond_1):
    """Build a condition map for the query."""
    condition = {}
    for i, key in enumerate(my_relation_tables):
        if join_conditions[i]:
            condition[key] = [join_conditions[i]]
        else:
            condition[key] = [dynamic_cond[i]]
            new_joining_cond[i].append(new_joining_cond_1[i][0])
            join_conditions.append(dynamic_cond[i][0])
    return condition


def finalize_query(tables, condition, join_types, join_types1):
    """Finalize the query by joining tables and conditions."""
    query = f"SELECT * FROM {tables[0]}"  # Start with the first table
    key_data = list(condition.keys())

    for i, table in enumerate(tables[1:], start=1):
        join_type = join_types[i - 1] if i - 1 < len(join_types) else 'inner'
        join_types1.append(join_type)
        query += f" {join_type} JOIN {table}"

        compare_value = key_data[i - 1]
        for index, cond in enumerate(condition[compare_value]):
            query += f" {'ON' if index == 0 else 'AND'} {cond[0]}"

    return query




