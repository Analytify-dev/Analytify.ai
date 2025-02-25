from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import psycopg2,cx_Oracle
from dashboard import models,serializers,roles,previlages,views,columns_extract,Connections,clickhouse
import pandas as pd
from sqlalchemy import text,inspect
import numpy as np
from .models import ServerDetails,ServerType,QuerySets,ChartFilters,DataSourceFilter
import ast,re,itertools
import datetime
import boto3,numpy
import json,os
from pytz import utc
import requests
from project import settings
import io
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain,zip_longest
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .Filters import connection_data_retrieve,server_details_check,literal_eval


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)


def calc_error_messages(query_set_id,field_name,user_id):
    if query_set_id=='' or query_set_id==None or query_set_id=="":
        return Response({'message':'empty queryset_id field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif field_name=='' or field_name==None or field_name=="":
        return Response({'message':'empty field_name field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return 200


# Function to remove table alias if it is the same as the table name
# def remove_tablealias_if_needed(ip1):
#     pattern = r'\"([^\"]+)\"\.\"([^\"]+)\"(?:\(([^)]+)\))?'
#     matches = re.findall(pattern, ip1)
#     modified_parts = []
#     for match in matches:
#         table_name = match[0]   
#         column_name = match[1]  
#         table_alias = match[2] 
#         if table_name in column_name:
#             output_string = column_name.replace(f"({table_name})", "").strip()
#             output_string = output_string.replace("()", "").strip()
#             modified_part = f'"{table_name}"."{output_string}"'
#         else:
#             modified_part = f'"{table_name}"."{column_name}"'
#         modified_parts.append(modified_part)
#     # Join all modified parts to form the final string
#     modified_string = " + ".join(modified_parts)
#     return modified_string


tb_cl_pattern = r'\"([^\"]+)\"\.\"([^\"]+)\"(?:\(([^)]+)\))?'
def remove_tablealias_if_needed(ip):
    def replacer(match):
        table_name = match.group(1)
        column_name = match.group(2)
        table_alias = match.group(3)
        # Remove alias if it matches the table name
        if table_name in column_name:
            output_string = column_name.replace(f"({table_name})", "").strip()
            output_string = output_string.replace("()", "").strip()
            return f'"{table_name}"."{output_string}"'
        else:
            return f'"{table_name}"."{column_name}({table_alias})"' if table_alias else f'"{table_name}"."{column_name}"'
    result = re.sub(tb_cl_pattern, replacer, ip)
    return result


def remove_table_names(input_string):
    return re.sub(r'"[\w_]+"', '', input_string)


def add_logic_to_query(base_query, logic_expression):
    # Check if the base query contains "FROM"
    base_query_lower = base_query.lower()
    if " from " not in base_query_lower:
        raise ValueError("The base query must include a FROM clause.")
    from_index = base_query_lower.index(" from ")
    select_part = base_query[:from_index].strip()  # Everything before "FROM"
    from_part = base_query[from_index:].strip()   # Everything from "FROM" onwards
    if select_part.endswith(","):
        modified_select = f"{select_part} {logic_expression}" # AS logic_value
    else:
        modified_select = f"{select_part}, {logic_expression}" #  AS logic_value
    final_query = f"{modified_select} {from_part}"
    return final_query



def calc_main_code(serializer,user_id,parameter):
    cal_field_id=serializer.validated_data['cal_field_id']
    query_set_id=serializer.validated_data['query_set_id']
    database_id1=serializer.validated_data['database_id']
    field_name=serializer.validated_data['field_name']
    nestedFunctionName=serializer.validated_data['nestedFunctionName']
    functionName=serializer.validated_data['functionName']
    actual_fields_logic=serializer.validated_data['actual_fields_logic']
    dragged_cal_field=serializer.validated_data['dragged_cal_field']
    error_msg=calc_error_messages(query_set_id,field_name,user_id)
    if not error_msg==200:
        return error_msg
    if QuerySets.objects.filter(user_id=user_id,queryset_id=query_set_id).exists():
        pass
    else:
        return Response({'message':'Invalid Queryset_id'},status=status.HTTP_406_NOT_ACCEPTABLE)
    pr_id=database_id1
    qrdt=models.QuerySets.objects.get(queryset_id=query_set_id)
    try:
        ser_dt,para=Connections.display_name(pr_id)
    except:
        return Response({'message':'Invalid Hierarchy Id'},status=status.HTTP_401_UNAUTHORIZED)
    try:
        clickhouse_class = clickhouse.Clickhouse(ser_dt.display_name)
        engine=clickhouse_class.engine
        cursor=clickhouse_class.cursor
    except:
        return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
    
    if dragged_cal_field==[] or dragged_cal_field==None or dragged_cal_field=='':
        actual_fields_logic_op=re.sub(r'"[\w_]+"(?=\.)', '', str(actual_fields_logic)).replace('.','')
        # actual_fields_logic_op=re.sub(r'"[^\.]+"\.', '', str(actual_fields_logic)).replace('.','')
        field_logic=remove_tablealias_if_needed(str(actual_fields_logic))
    else:
        drcl_1 = literal_eval(dragged_cal_field)
        fn_list=[]
        logic_list=[]
        for clid in drcl_1:
            try:
                cl_tb=models.calculation_field.objects.get(id=clid)
            except:
                return Response({'message':'calculation id not exists'},status=status.HTTP_404_NOT_FOUND)

            ## to fetch only columnnames 
            save_output=re.sub(r'"[\w_]+"(?=\.)', '', str(actual_fields_logic)).replace('.','') # from input data
            fn_save_output=re.sub(r'"[\w_]+"(?=\.)', '', str(cl_tb.actual_dragged_logic)).replace('.','') # from cal_field
            # save_output=re.sub(r'"[^\.]+"\.', '', str(actual_fields_logic)).replace('.','') # from input data
            # fn_save_output=re.sub(r'"[^\.]+"\.', '', str(cl_tb.actual_dragged_logic)).replace('.','') # from cal_field
            appen_dt = '('+fn_save_output+')'
            # appending in place of cal_field
            if fn_list==[]:
                output_field=str(save_output).replace(f'"{cl_tb.field_name}"',appen_dt)
            else:
                output_field = [item.replace(f'"{cl_tb.field_name}"', appen_dt) for item in fn_list]
            fn_list.clear()
            fn_list.append(output_field)
        
            ## to fetch only tablename.columnnames
            table_output=remove_tablealias_if_needed(str(actual_fields_logic)) # from input data
            field_logic_ckeck=remove_tablealias_if_needed(str(cl_tb.actual_dragged_logic))# from cal_field
            appen_dt_check = '('+field_logic_ckeck+')'
            # appending in place of cal_field
            if logic_list==[]:
                output_field=str(table_output).replace(f'"{cl_tb.field_name}"',appen_dt_check)
            else:
                output_field = [item.replace(f'"{cl_tb.field_name}"', appen_dt_check) for item in logic_list]
            logic_list.clear()
            logic_list.append(output_field)
        actual_fields_logic_op = fn_list[0][0]
        field_logic = logic_list[0][0]
    # print(actual_fields_logic)
    # print(actual_fields_logic_op)
    # print(field_logic)
    query = qrdt.custom_query
    # print(query)
    if qrdt.is_custom_sql==True:
        modified_query=add_logic_to_query(query, actual_fields_logic_op)
        # print(modified_query)
    else:
        pattern = r'(?i)(select\s+)(.*?)(\s+from\s+)'
        try:
            modified_query = re.sub(pattern, rf'\1{field_logic}\3', query, count=1)
        except:
            modified_query = re.sub(pattern,lambda match: f"{match.group(1)}{field_logic}{match.group(3)}", query, count=1)
    
    try:
        result=views.query_execute(modified_query,cursor,para)
    except Exception as e:
        return Response({'error':str(e).splitlines()[0]},status=status.HTTP_400_BAD_REQUEST)
    if parameter=='SAVE':
        models.calculation_field.objects.create(user_id=user_id,queryset_id=query_set_id,hierarchy_id=pr_id,
                                                field_name=field_name,cal_logic=actual_fields_logic_op,actual_dragged_logic=actual_fields_logic,
                                                nestedFunctionName=nestedFunctionName,functionName=functionName,created_at=created_at,
                                                updated_at=updated_at)
        return Response({"message":"Created Successfully"},status=status.HTTP_200_OK)
    elif parameter=='UPDATE':
        if cal_field_id==None or cal_field_id=='' or cal_field_id=="":
            return Response({"message":"Empty calculation field id is not acceptable"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            models.calculation_field.objects.filter(user_id=user_id,id=cal_field_id).update(queryset_id=query_set_id,actual_dragged_logic=actual_fields_logic,
            hierarchy_id=pr_id,field_name=field_name,cal_logic=actual_fields_logic_op,nestedFunctionName=nestedFunctionName,functionName=functionName,updated_at=updated_at)
            return Response({"message":"Updated Successfully"},status=status.HTTP_200_OK)
    else:
        return Response({'message':'Not allowed'},status=status.HTTP_400_BAD_REQUEST)


##### Create a calculated field
class calculated_field_api(CreateAPIView):
    serializer_class=serializers.calculated_field

    @transaction.atomic
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                query_set_id=serializer.validated_data['query_set_id']
                field_name=serializer.validated_data['field_name']
                if models.calculation_field.objects.filter(user_id=tok1['user_id'],queryset_id=query_set_id,field_name=field_name).exists():
                    return Response({'message':'Calculation field name already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass
                fn_output=calc_main_code(serializer,tok1['user_id'],parameter='SAVE')
                return fn_output
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])     


    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                cal_field_id=serializer.validated_data['cal_field_id']
                field_name=serializer.validated_data['field_name']
                query_set_id=serializer.validated_data['query_set_id']
                cal_tb=models.calculation_field.objects.get(user_id=tok1['user_id'],id=cal_field_id)
                if cal_tb.field_name==field_name:
                    pass
                else:
                    if models.calculation_field.objects.filter(user_id=tok1['user_id'],queryset_id=query_set_id,field_name=field_name).exists():
                        return Response({'message':'Calculation field name already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        pass
                fn_output=calc_main_code(serializer,tok1['user_id'],parameter='UPDATE')
                return fn_output
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
     
        
@api_view(['GET'])
@transaction.atomic
@csrf_exempt
def get_cal_fields(request,cal_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            tb_values=models.calculation_field.objects.filter(user_id=tok1['user_id'],id=cal_id).values().order_by('-updated_at')
            return Response(tb_values,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method Not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['DELETE'])
@transaction.atomic
@csrf_exempt
def del_cal_fields(request,cal_id,token):
    if request.method=='DELETE':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            tb_values=models.calculation_field.objects.filter(user_id=tok1['user_id'],id=cal_id).delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method Not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


def cal_data(user_id,cal_id):
    final_li=[]
    for cl_id in cal_id:
        try:
            tb_values=models.calculation_field.objects.get(user_id=user_id,id=cl_id)
            data = {
                'status':200
            }
        except:
            data = {
                'status':404,
                'message':'Data not exists'
            }
        cleaned_string = str(tb_values.cal_logic).replace('_1', '')
        # cleaned_data = re.sub(r'\(.*?\)', '', cleaned_string)

        qrtb=models.QuerySets.objects.get(queryset_id=tb_values.queryset_id)
        ser_db_data=models.ServerDetails.objects.get(id=qrtb.server_id)
        ser_data=models.ServerType.objects.get(id=ser_db_data.server_type)
        connect1=columns_extract.server_connection(ser_db_data.username,ser_db_data.password,ser_db_data.database,ser_db_data.hostname,ser_db_data.port,ser_db_data.service_name,ser_data.server_type.upper(),ser_db_data.database_path)
        if connect1['status']==200:
            engine=connect1['engine']
            cursor=connect1['cursor']
        else:
            data = {
                'status':connect1['status'],
                'message':connect1['message']
            }
            # return Response({"message":connect1['message']},status=connect1['status'])
        
        # formula_pase=parse_formula_with_pyparsing(cleaned_string)
        # print(formula_pase)

        pattern = r'\[(\w+)\.(\w+)\]\s*([\+\-\*/])\s*\[(\w+)\.(\w+)\((\w+)\)\]'
        pattern1 = r'\[(\w+)\.(\w+)\]\s*([\+\-\*/])\s*\[(\w+)\.(\w+)\]'
        pattern2 = r'\[([\w_]+)\."([a-zA-Z0-9_()]+(?:\(([a-zA-Z0-9_]+)\))?)"\]\s*([\+\-\*/])\s*\[([\w_]+)\."([a-zA-Z0-9_()]+(?:\(([a-zA-Z0-9_]+)\))?)"\]'
        match = re.search(pattern, cleaned_string)
        match1 = re.search(pattern1, cleaned_string)
        match2 = re.search(pattern2, cleaned_string)
        if match:
            table1, column1, operator, table2, column2, alias2 = match.groups()
        elif match1:
            table1, column1, operator, table2, column2 = match1.groups()
        elif match2:
            table1, column1, alias1, operator, table2, column2, alias2 = match2.groups()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if table1==table2:
            query = f"SELECT {column1} {operator} {column2} AS result FROM {table1}"
        else:
            query = f"SELECT {table1}.{column1} {operator} {table2}.{column2} AS result FROM {table1} JOIN {table2} ON {table1}.{column1} = {table2}.{column2}"
        result=cursor.execute(text(query))
        l1=[]
        for row in result:
            l1.append(str(row).replace('(','').replace(')','').replace(',',''))
            d1 = {'result_data':l1}
        final_li.append(d1)
    data = {
        'status':200,
        'data':final_li
    }
    return data
    # return Response(l1,status=status.HTTP_200_OK)