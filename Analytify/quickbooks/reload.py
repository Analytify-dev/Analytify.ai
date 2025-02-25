
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import psycopg2,cx_Oracle
from dashboard import models,serializers,roles,previlages,views,columns_extract,clickhouse,Connections
import pandas as pd
from sqlalchemy import text,inspect
import numpy as np
# from ..dashboard.models import ServerDetails,ServerType,QuerySets,ChartFilters,DataSourceFilter
import ast,re,itertools
import datetime
from quickbooks import models as qb_models,connectwise,halops,salesforce,shopify,salesforce_endpoints,views as qb_views
import boto3
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
from .googlesheets import reinject_google_sheets_data

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)

@transaction.atomic()
def data_re_injecting(ser_dt,parameter,tok1):
    # if not parameter=='files':
    if parameter=='salesforce':
        parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='salesforce')
        token_status=salesforce_endpoints.salesforce_token(parent_ids.id,tok1)
        if not token_status['status']==200:
            para=400
            return Response({'message':'session expired, login to salesforce again',"salesforceConnected":False,},status=token_status['status'])
        else:
            para=200
    elif parameter=='quickbooks':
        parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='quickbooks')
        token_status=qb_views.quickbooks_token(parent_ids.id,tok1)
        if not token_status['status']==200:
            para=400
            return Response({'message':'session expired, login to quickbooks again',"quickbooksConnected":False,},status=token_status['status'])
        else:
            para=200
    elif parameter=='files':
        para=400
    else:
        para=200
    if para==200:
        # TRUNCATE ALL TABLES FROM  db
        click = clickhouse.Clickhouse()
        click.cursor.execute(text(f'TRUNCATE ALL TABLES FROM \"{ser_dt.display_name}\"'))
        print(f'{ser_dt.display_name}'" Deleted successfully")
    else:
        pass

    if parameter.upper() in columns_extract.servers_list:
        server_conn=columns_extract.server_connection(ser_dt.username, ser_dt.password, ser_dt.database, ser_dt.hostname,ser_dt.port,ser_dt.service_name, parameter.upper(), ser_dt.server_type)
        if server_conn['status']==200:
            deco_password=views.decode_string(ser_dt.password)
            data = click.migrate_database_to_clickhouse(server_conn['cursor'],parameter.lower(),ser_dt.display_name,ser_dt.username,deco_password,ser_dt.database,ser_dt.hostname,ser_dt.port,ser_dt.service_name,parameter.upper(),ser_dt.server_type)
            return 200
        else:
            return Response({'message':server_conn['message']},status=server_conn['status']) 
    elif parameter in columns_extract.ser_list:
        if parameter=='connectwise':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='connectwise')
            result=click.json_to_table(connectwise.apicn_urls,tok1,parent_ids.id,ser_dt.display_name,'connectwise')
        elif parameter=='halops':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='halops')
            result=click.json_to_table(halops.apicn_urls,tok1,parent_ids.id,ser_dt.display_name,'halops')
        elif parameter=='salesforce':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='salesforce')
            result=click.json_to_table(salesforce.salesforce_tables,tok1,parent_ids.id,ser_dt.display_name,'salesforce')
        elif parameter=='quickbooks':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='quickbooks')
            result=click.json_to_table(qb_views.qb_urls,tok1,parent_ids.id,ser_dt.display_name,'quickbooks')
        elif parameter=='shopify':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='shopify')
            result=click.json_to_table(shopify.api_urls,tok1,parent_ids.id,ser_dt.display_name,'shopify')
        elif parameter=='google_sheets':
            parent_ids=models.parent_ids.objects.get(table_id=ser_dt.id,parameter='google_sheets')
            result = reinject_google_sheets_data(parameter, tok1, parent_ids.id)
            if result["status"] != 200:
                return Response({"error": result.get("error", "Reinjection failed")}, 
                            status=result["status"])
            # result=click.json_to_table(shopify.api_urls,tok1,parent_ids.id,ser_dt.display_name,'google_sheets')
        else:
            return Response({'message':'Invalid server type'},status=status.HTTP_406_NOT_ACCEPTABLE)
        if result['status']==200:
            return 200
        else:
            return Response({'message':str(result)},status=result['status'])
    elif parameter.upper()=='FILES':
        return 200
    else:
        return Response({'message':'Invalid server type'},status=status.HTTP_406_NOT_ACCEPTABLE)
    # else:
    #     return Response({'message':'Files are not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
                

@api_view(['GET'])
def data_reload(request,token,dsh_id):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            dashbaord_data=models.dashboard_data.objects.get(id=dsh_id)
            data=[]
            for sh in Connections.litera_eval(dashbaord_data.sheet_ids):
                sheet_data=models.sheet_data.objects.get(id=sh)
                sh_flt_id=models.SheetFilter_querysets.objects.get(Sheetqueryset_id=sheet_data.sheet_filt_id)
                ser_dt,para=Connections.display_name(sh_flt_id.hierarchy_id)
                data_injecting=data_re_injecting(ser_dt,para,tok1)
                if not data_injecting==200:
                    return data_injecting
                try:
                    clickhouse_class = clickhouse.Clickhouse(ser_dt.display_name)
                    engine=clickhouse_class.engine
                    cursor=clickhouse_class.cursor
                except:
                    return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
                if para.upper()=="MICROSOFTSQLSERVER":
                    query = "{}".format(sh_flt_id.custom_query)
                    fn_qr=Connections.remove_aggregations(query)
                    query1=fn_qr.replace(':ok','').replace(':OK','')
                    result=cursor.execute(query1)
                    codes = cursor.description
                    columns = [col[0] for col in codes]  # Step 2: Get column names
                    rows = result.fetchall()
                elif para.upper()=="SNOWFLAKE":
                    # quoted_query = fn_data.custom_query.replace('"', '')
                    fn_qr=Connections.remove_aggregations(sh_flt_id.custom_query)
                    result=cursor.execute(text(fn_qr))
                    codes=result.cursor.description
                    columns = [col[0] for col in codes]  # Step 2: Get column names
                    rows = result.fetchall()
                else:
                    fn_qr=Connections.remove_aggregations(sh_flt_id.custom_query)
                    result=cursor.execute(text(fn_qr))
                    codes=result.cursor.description
                    columns = [col[0] for col in codes]  # Step 2: Get column names
                    rows = result.fetchall()

                d1=[]
                fn_col=[]
                fn_row=[]
                for i in rows:
                    a = list(i)
                    d1.append(a)
                result_data=[]
                for idx, col in enumerate(columns):
                    column_data = [row[idx] for row in d1]
                    result_data.append({
                        "col": col,
                        "rows_data": column_data
                    })
                #
                for item in result_data:
                    item['col'] = item['col'].replace(':ok', '').replace(':OK', '').replace('1','')
                    if item["col"] in sh_flt_id.columns:
                        fn_col.append(item)
                    elif item["col"] in sh_flt_id.rows:
                        fn_row.append(item)
                #
                f_res={
                    "status":200,
                    "data":{'col':fn_col,'row':fn_row}
                }
                data.append(f_res)
                # cursor.close()
                # engine.dispose()
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
