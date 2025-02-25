
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import psycopg2,cx_Oracle
from dashboard import models,serializers,roles,previlages,views,columns_extract,clickhouse
import pandas as pd
from sqlalchemy import text,inspect
import numpy as np
from .models import ServerDetails,ServerType,QuerySets,ChartFilters,DataSourceFilter
import ast,re,itertools
import datetime
from quickbooks import models as qb_models
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

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)

##############################################################################################################################

def table_name_from_query(quer_tb):
    join_list=['left','in','right','self','inner','join']
    if quer_tb.is_custom_sql==False:
        pattern = re.compile(r'FROM\s+"?(\w+)"?\."?(\w+)"?|JOIN\s+"?(\w+)"?\."?(\w+)"?', re.IGNORECASE)
        matches = pattern.findall(quer_tb.custom_query)
        al_patern=re.compile(r'(?:FROM|JOIN)\s+(?:"?\w+"?\.)?"?\w+"?\s+(\w+)', re.IGNORECASE) # to fetch table alias
        # al_patern=re.compile(r'(?:FROM|JOIN)\s+(?:"?\w+"?\.)?"?\w+"?\s+(\w+)\s*(?!LEFT|RIGHT|SELF|INNER|ON)\b',) 
        mt=al_patern.findall(quer_tb.custom_query)
        table_names = []
        schema_names = []
        for match in matches:
            schema, table = match[0], match[1]
            if schema and table:
                table_names.append(table)
                schema_names.append(schema)
            schema, table = match[2], match[3]
            if schema and table:
                table_names.append(table) # table_names
                schema_names.append(schema) # schema names
        matching_keywords = [keyword for keyword in mt if keyword in join_list]
        if matching_keywords!=[]:
            mt12 = []
        else:
            mt12 = mt
        data = {
            "tables":table_names,
            "schemas":schema_names,
            "table_alias":mt12
        }
        return data
    else:
        pattern1 = re.compile(r'(FROM|JOIN)\s+"?(\w+)"?\."?(\w+)"?', re.IGNORECASE)   
        matches1 = pattern1.findall(quer_tb.custom_query)
        schemas = []
        tables = []
        for match in matches1:
            if len(match) == 3:
                schemas.append(match[1])
                tables.append(match[2])
        pattern2 = re.compile(r'FROM\s+([^\s;]+)|JOIN\s+([^\s;]+)', re.IGNORECASE)
        matches2 = pattern2.findall(quer_tb.custom_query)
        schemas1=[]
        tables1 = []
        for match in matches2:
            tables1.append(match[0].lower())
        al_patern=re.compile(r'(?:FROM|JOIN)\s+(?:"?\w+"?\.)?"?\w+"?\s+(\w+)', re.IGNORECASE) # to fetch table alias
        mt=al_patern.findall(quer_tb.custom_query)
        matching_keywords = [keyword for keyword in mt if keyword in join_list]
        if matching_keywords!=[]:
            mt123=[]
        else:
            mt123=mt
        if schemas!=[]:
            data = {
                "tables":tables,
                "schemas":schemas,
                "table_alias":mt123
            }
        else:
            data = {
                "tables":tables1,
                "schemas":schemas1,
                "table_alias":mt123
            }
        return data
    

def litera_eval(data):
    if data==None or data=="":
        data1 = data
    else:
        data1=ast.literal_eval(data)
    return data1

def remove_aggregations(query):
    pattern = r'(SUM|AVG|MIN|MAX|COUNT)\("([^"]+)"\)(?:\s+AS\s+"([^"]+)")?'
    group_by_columns = set()
    def replace_aggregation(match):
        _, column_name, alias = match.groups()
        if 'date' in column_name.lower() or (alias and 'date' in alias.lower()):
            group_by_columns.add(f'"{column_name}"')
            return f'"{column_name}"'
        else:
            return match.group(0)
    new_query = re.sub(pattern, replace_aggregation, query, flags=re.IGNORECASE)
    group_by_pattern = re.compile(r'(GROUP\s+BY\s+)([^;]+)', re.IGNORECASE)
    group_by_match = group_by_pattern.search(new_query)
    if group_by_match:
        current_group_by = group_by_match.group(2).strip()
        updated_group_by = ', '.join(sorted(set(current_group_by.split(', ')) | group_by_columns))
        new_query = new_query[:group_by_match.start(2)] + updated_group_by + new_query[group_by_match.end(2):]
    else:
        if group_by_columns:
            new_query += f' GROUP BY {", ".join(sorted(group_by_columns))}'
    return new_query

def data_reload(data):
    sh_fl_id=data.sheet_filt_id
    fn_data=models.SheetFilter_querysets.objects.get(Sheetqueryset_id=sh_fl_id)
    s_id=data.server_id
    f_id=data.file_id
    d1=[]
    result_data=[]
    fn_col=[]
    fn_row=[]
    if s_id==None or s_id=='' or s_id=="":
        f_data=models.FileDetails.objects.get(id=f_id)
        file_data=models.FileType.objects.get(id=f_data.file_type)
        files_data = columns_extract.file_details(file_data.file_type,f_data)
        if files_data['status']==200:
            engine=files_data['engine']
            cursor=files_data['cursor']
            # fn_qr=remove_aggregations(fn_data.custom_query)
            result=cursor.execute(text(fn_data.custom_query))
            codes=result.cursor.description
            columns = [col[0] for col in codes]  # Step 2: Get column names
            rows = result.fetchall()
        else:
            f_res={
                "status":files_data['status'],
                "message":files_data['message']
            }
            return f_res
    else:
        s_data=models.ServerDetails.objects.get(id=s_id)
        s_type=models.ServerType.objects.get(id=s_data.server_type)
        server_path=''
        try:
            clickhouse_class = clickhouse.Clickhouse(s_data.display_name)
            engine=clickhouse_class.engine
            cursor=clickhouse_class.cursor
        except:
            return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
        d1=[]
        if s_type.server_type.upper()=="MICROSOFTSQLSERVER":
            query = "{}".format(fn_data.custom_query)
            fn_qr=remove_aggregations(query)
            query1=fn_qr.replace(':ok','').replace(':OK','')
            result=cursor.execute(query1)
            codes = cursor.description
            columns = [col[0] for col in codes]  # Step 2: Get column names
            rows = result.fetchall()
        elif s_type.server_type.upper()=="SNOWFLAKE":
            # quoted_query = fn_data.custom_query.replace('"', '')
            fn_qr=remove_aggregations(fn_data.custom_query)
            result=cursor.execute(text(fn_qr))
            codes=result.cursor.description
            columns = [col[0] for col in codes]  # Step 2: Get column names
            rows = result.fetchall()
        else:
            fn_qr=remove_aggregations(fn_data.custom_query)
            result=cursor.execute(text(fn_qr))
            codes=result.cursor.description
            columns = [col[0] for col in codes]  # Step 2: Get column names
            rows = result.fetchall()

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
        if item["col"] in fn_data.columns:
            fn_col.append(item)
        elif item["col"] in fn_data.rows:
            fn_row.append(item)
    #
    f_res={
        "status":200,
        "data":{'col':fn_col,'row':fn_row}
    }
    cursor.close()
    # engine.dispose()
    return f_res

##### Show_me from table,column
class show_me(CreateAPIView):
    serializer_class=serializers.show_me_input

    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_sheet,previlages.view_sheet,previlages.edit_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                db_id=serializer.validated_data['db_id']
                col=serializer.validated_data['col']
                row=serializer.validated_data['row']
                for i1 in row:
                    col.append(i1)
                column_name=[]
                data_types=[]
                for i1 in col:
                    column_name.append(i1[0])
                    data_types.append(i1[1])
            else:
                return Response({'message':"Serializer Error"},status=status.HTTP_406_NOT_ACCEPTABLE)
            # try:
            #     ser_db_data=models.ServerDetails.objects.get(id=db_id)
            # except:
            #     return Response({'message':'server_details_id/server_type not exists'},status=status.HTTP_404_NOT_FOUND)
            charts=[]
            ids=[]
            ints=["int","float","number","num","numeric","INT","FLOAT","NUMBER","NUM","NUMERIC"]
            dates=["datetime","date","DATETIME","DATE"]
            measures = [col for col, dtype in zip(column_name, data_types) if dtype in ints]
            datetime_dt = [col for col, dtype in zip(column_name, data_types) if dtype in dates]
            dimensions = [col for col, dtype in zip(column_name, data_types) if dtype not in ints]
            if len(measures)!=0 and len(dimensions)!=0:
                char=models.charts.objects.filter(min_measures__lte=len(measures),min_dimensions__lte=len(dimensions),max_dimensions__lte=len(dimensions),max_measures__lte=len(measures)).values()
            elif len(measures)!=0 and len(dimensions)==0:
                char=models.charts.objects.filter(min_measures__lte=len(measures),min_dimensions__gte=len(dimensions),max_dimensions__lte=len(dimensions),max_measures__lte=len(measures)).values()
            elif len(measures)==0 and len(dimensions)!=0:
                char=models.charts.objects.filter(min_measures__gte=len(measures),min_dimensions__lte=len(dimensions),max_dimensions__lte=len(dimensions),max_measures__lte=len(measures)).values()                        
            elif len(measures)==0 and len(dimensions)==0:
                char=models.charts.objects.filter(min_measures__gte=len(measures),min_dimensions__gte=len(dimensions),max_dimensions__lte=len(dimensions),max_measures__lte=len(measures)).values()
            elif len(measures)!=0 and len(datetime_dt)!=0: 
                char=models.charts.objects.filter(min_measures__lte=len(measures),min_dates__lte=len(datetime_dt),max_dates__lte=len(datetime_dt),max_measures__lte=len(measures)).values()  
            elif len(dimensions)!=0 and len(datetime_dt)!=0: 
                char=models.charts.objects.filter(min_dimensions__lte=len(dimensions),min_dates__lte=len(datetime_dt),max_dimensions__gte=len(dimensions),max_dates__gte=len(datetime_dt)).values()  
            elif len(measures)==0 and len(datetime_dt)!=0: 
                char=models.charts.objects.filter(min_measures__gte=len(measures),min_dates__lte=len(datetime_dt),max_measures__lte=len(measures),max_dates__lte=len(datetime_dt)).values()  
            elif len(dimensions)==0 and len(datetime_dt)!=0: 
                char=models.charts.objects.filter(min_dimensions__gte=len(dimensions),min_dates__lte=len(datetime_dt),max_dimensions__lte=len(dimensions),max_dates__lte=len(datetime_dt)).values() 
            else:
                pass 
            defl=[24,17,13,1,6]
            def2=["pie","AREA_CHARTS","line","bar","Table"]
            for i12,i2 in zip(defl,def2):
                ids.append(i12)
                charts.append(i2)
            for ch in char:
                ids.append(ch['id'])
                charts.append(ch['chart_type'])
            id_se=(set(ids))
            ch_se=(set(charts))
            data = [{"id":ids1,"charts":chart1} for ids1,chart1 in zip(list(id_se),list(ch_se))]
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])


##########    Sheet data saving,update,delete & Sheet Name update  ##################

try:
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
except Exception as e:
    print(e)


def file_save_1(data,server_id,queryset_id,ip,dl_key):
    if settings.file_save_path=='s3':
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')
        file_path = f'{t1}{server_id}{queryset_id}.txt'
        # with open(file_path, 'w') as file:
        #     json.dump(data, file, indent=4)
        json_data = json.dumps(data, indent=4)
        file_buffer = io.BytesIO(json_data.encode('utf-8'))
        file_key = f'insightapps/{ip}/{file_path}'
        if dl_key=="":
            s3.upload_fileobj(file_buffer, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        else:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(dl_key))
            s3.upload_fileobj(file_buffer, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        data_fn={
            "file_key":file_key,
            "file_url":file_url
        }
        return data_fn
    else:
        if dl_key=="" or dl_key==None:
            pass
        else:
            delete_file(str(dl_key))
        
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')
        file_path = f'insightapps/{ip}/{t1}.txt'
        json_data = json.dumps(data, indent=4)
        with default_storage.open(file_path, 'w') as file:
            file.write(json_data)
        file_url = f"{settings.file_save_url}media/{file_path}"
        data_fn={
            "file_key":file_path,
            "file_url":file_url
        }
        return data_fn


def file_files_save(file_path,file_path112):
    if settings.file_save_path=='s3':
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')+str(file_path)
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')+'_IN_'+str(file_path)
        file_path1 = f'insightapps/files/{t1}'
        try:
            s3.upload_fileobj(file_path112, settings.AWS_STORAGE_BUCKET_NAME, file_path1)
        except:
            try:
                with open(file_path112.temporary_file_path(), 'rb') as data:  ## read that binary data in a file(before replace file data)
                    s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1)  ## pass that data in data and replaced file name in file key.
            except:
                data = ContentFile(file_path112.read())
                s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1)
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_path1}"
        data_fn={
            "file_key":file_path1,
            "file_url":file_url
        }
        return data_fn
    else:
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')+str(file_path)
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')+'_IN_'+str(file_path)
        file_path1 = f'insightapps/files/{t1}'   
        # with default_storage.open(file_path112, 'w') as file:
        #     file.write(file_path1)   
        file_content = ContentFile(file_path112.read())
        default_storage.save(file_path1, file_content)
        file_url = f"{settings.file_save_url}media/{file_path1}"
        data_fn={
            "file_key":file_path1,
            "file_url":file_url
        }
        return data_fn  


def image_save_1(image,ip,dl_key):
    if settings.file_save_path=='s3':
        if image==None or image=='':
            data_fn = {
                "file_key":None,
                "file_url":None
            }
            return data_fn
        else:
            # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')
            t1=str(datetime.datetime.now()).replace(' ','_')
            file_path = f'{t1}{image}'
            file_key = f'insightapps/{ip}/{file_path}'
            if dl_key=="" or dl_key==None:
                s3.upload_fileobj(image, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
                file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
            else:
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(dl_key))
                s3.upload_fileobj(image, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
                file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
            data_fn={
                "file_key":file_key,
                "file_url":file_url
            }
            return data_fn
    else:
        if image==None or image=='':
            data_fn = {
                "file_key":None,
                "file_url":None
            }
            return data_fn
        else:
            if dl_key=="" or dl_key==None:
                pass
            else:
                delete_file(str(dl_key))

            # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')+str(image)
            t1=str(datetime.datetime.now()).replace(' ','_')+str(image)
            file_path = f'insightapps/{ip}{t1}'
            default_storage.save(file_path, ContentFile(image.read()))   
            file_url = f"{settings.file_save_url}media/{file_path}"
            data_fn={
                "file_key":file_path,
                "file_url":file_url
            }
            return data_fn
    

def delete_file(data):
    try: 
        a1='media/'+str(data)
        os.remove(a1)
    except:
        pass


@api_view(['GET'])
@transaction.atomic
def is_public(request,ds_id):
    if request.method=='GET':
        if models.dashboard_data.objects.filter(id=ds_id).exists():
            models.dashboard_data.objects.filter(id=ds_id).update(is_public=True,updated_at=updated_at)
            return Response({'message':'added to public dashboard'},status=status.HTTP_200_OK)
        else:
            return Response({'message':'dashboard Not exists'},status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

def sheet_filter_queryset(serializer,user_id,parameter):
    col = serializer.validated_data['col']
    row = serializer.validated_data['row']
    query_set_id  = serializer.validated_data['queryset_id']
    datasource_querysetid = serializer.validated_data['datasource_querysetid']
    sheetfilter_querysets_id = serializer.validated_data['sheetfilter_querysets_id']
    filter_id = serializer.validated_data["filter_id"]
    server_id1 = serializer.validated_data['server_id']
    custom_query = serializer.validated_data['custom_query']
    pivot_measure=serializer.validated_data['pivot_measure']

    pr_id=server_id1
    if parameter=='SAVE' and sheetfilter_querysets_id is None or sheetfilter_querysets_id == '':
        abc1 = models.SheetFilter_querysets.objects.create(
            datasource_querysetid = datasource_querysetid,
            queryset_id  = query_set_id,
            user_id = user_id,
            hierarchy_id=pr_id,
            filter_id_list = filter_id,
            custom_query = custom_query,
            columns  = col,
            rows = row,
            pivot_measure = pivot_measure,
            updated_at = updated_at,
            created_at = created_at
        )
        id = abc1.pk
    elif parameter=='UPDATE' and sheetfilter_querysets_id != None or sheetfilter_querysets_id != '':
        abc1 = models.SheetFilter_querysets.objects.filter(Sheetqueryset_id =sheetfilter_querysets_id,user_id= user_id).update(
            queryset_id  = query_set_id,
            datasource_querysetid = datasource_querysetid,
            user_id = user_id,
            filter_id_list = filter_id,
            custom_query = custom_query,
            columns  = col,
            pivot_measure = pivot_measure,
            rows = row,
            updated_at = updated_at
        )
        sfid=models.SheetFilter_querysets.objects.get(Sheetqueryset_id =sheetfilter_querysets_id,user_id= user_id)
        id = sfid.Sheetqueryset_id
    return id

def sheet_s_u(serializer,u_id,sh_id,parameter):
    data=serializer.validated_data['data']
    chart_id=serializer.validated_data['chart_id']
    queryset_id=serializer.validated_data['queryset_id']
    server_id1=serializer.validated_data['server_id']
    sheet_name=serializer.validated_data['sheet_name']
    filterId=serializer.validated_data['filter_id']
    sheet_tag_name=serializer.validated_data['sheet_tag_name']
    sheetfilter_querysets_id=serializer.validated_data['sheetfilter_querysets_id']
    
    status1,tb_id,parameter1=columns_extract.parent_id(server_id1)
    pr_id=server_id1
    server_id=tb_id
    if status1 != 200:
        return Response({'message':'Invalid Id'},status=status1)
    if sheet_name=='' or sheet_name==None or sheet_name=="" or sheet_name==' ':
        return Response({'message':'Empty sheet_name field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        pass
    if models.charts.objects.filter(id=chart_id).exists():
        pass
    else:
        return Response({'message':'Chart id not exists'},status=status.HTTP_404_NOT_FOUND)
    if server_id==None:
        server_id='server_id'
    if parameter=="save":
        if models.sheet_data.objects.filter(user_id=u_id,queryset_id=queryset_id,hierarchy_id=pr_id,sheet_name=sheet_name).exists() or models.sheet_data.objects.filter(queryset_id=queryset_id,hierarchy_id=pr_id,user_ids__contains=u_id,sheet_name=sheet_name).exists():
            return Response({'message':'Sheet Name already exists, please rename the sheet name'},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            dl_key=""
            file_sv=file_save_1(data,server_id,queryset_id,ip='sheetdata',dl_key=dl_key)
            sheet_fil_qid=sheet_filter_queryset(serializer,u_id,parameter='SAVE')
            sh123=models.sheet_data.objects.create(user_id=u_id,chart_id=chart_id,queryset_id=queryset_id,hierarchy_id=pr_id,filter_ids=filterId,sheet_filt_id=sheet_fil_qid,
                                                datapath=file_sv["file_key"],datasrc=file_sv["file_url"],created_at=created_at,updated_at=updated_at,
                                                sheet_name=sheet_name,sheet_tag_name=sheet_tag_name)
            models.sheet_data.objects.filter(id=sh123.id).update(created_at=created_at,updated_at=updated_at)
            return Response({"sheet_id":sh123.id,"sheet_name":sh123.sheet_name,'message':'Saved Successfully'},status=status.HTTP_200_OK)
    elif parameter=="update":
        if models.sheet_data.objects.filter(queryset_id=queryset_id,hierarchy_id=pr_id,id=sh_id).exists(): # user_id=u_id,
        # or models.sheet_data.objects.filter(user_ids__contains=u_id,queryset_id=queryset_id,server_id=server_id,id=sh_id).exists():
            if sheetfilter_querysets_id==None or sheetfilter_querysets_id=='':
                return Response({'message':'empty sheetfilter_queryset_id is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                sheet_fil_qid=sheet_filter_queryset(serializer,u_id,parameter='UPDATE')
            old= models.sheet_data.objects.get(id=sh_id)
            if sheetfilter_querysets_id==None or sheetfilter_querysets_id=='':
                return Response({'message':'empty sheetfilter_queryset_id is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                sheet_fil_qid=sheet_filter_queryset(serializer,u_id,parameter='UPDATE')
            if old.sheet_name==sheet_name:
                pass
            else:
                if models.sheet_data.objects.filter(queryset_id=queryset_id,hierarchy_id=pr_id,sheet_name=sheet_name).exists(): #user_id=u_id,
                    # or models.sheet_data.objects.filter(user_ids__contains=u_id,queryset_id=queryset_id,server_id=server_id,sheet_name=sheet_name).exists():
                    return Response({'message':'Sheet name already exists for this queryset, data and sheet name will not update'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass
            file_sv=file_save_1(data,server_id,queryset_id,ip='sheetdata',dl_key=old.datapath)
            models.sheet_data.objects.filter(queryset_id=queryset_id,hierarchy_id=pr_id,id=sh_id).update(sheet_name=sheet_name,filter_ids=filterId,
                chart_id=chart_id,datapath=file_sv["file_key"],datasrc=file_sv["file_url"],updated_at=updated_at,sheet_filt_id=sheet_fil_qid,
                sheet_tag_name=sheet_tag_name)
            models.sheet_data.objects.filter(id=sh_id).update(updated_at=updated_at)
            return Response({'message':'Updated Successfully'},status=status.HTTP_200_OK)
        else:
            return Response({'message':'Sheet not exists'},status=status.HTTP_404_NOT_FOUND)
    else:
        pass

class sheet_saving(CreateAPIView):
    serializer_class=serializers.sheet_save_serializer

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_sheet,previlages.create_sheet_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                shid=""
                sh12 = sheet_s_u(serializer,tok1['user_id'],shid,parameter="save")
                return sh12
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

class sheet_update(CreateAPIView):
    serializer_class=serializers.sheet_save_serializer

    def post(self,request,token,shid):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_sheet,previlages.edit_sheet_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                sh12 = sheet_s_u(serializer,tok1['user_id'],shid,parameter="update")
                return sh12
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
     

class sheet_retrieve(CreateAPIView):
    serializer_class=serializers.sheet_retrieve_serializer

    @transaction.atomic
    def post(self,request,shid,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_sheet,previlages.edit_sheet,previlages.view_sheet_filters])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            ch_list=[]
            if serializer.is_valid(raise_exception=True):  
                queryset_id=serializer.validated_data['queryset_id']
                server_id1=serializer.validated_data['server_id']
                status1,tb_id,parameter=columns_extract.parent_id(server_id1)
                pr_id=server_id1
                if status1 != 200:
                    return Response({'message':'Invalid Id'},status=status1)
                try:
                    try:
                        sheetdata=models.sheet_data.objects.get(queryset_id=queryset_id,hierarchy_id=pr_id,id=shid)#user_id=tok1['user_id'],
                    except:
                        sheetdata=models.sheet_data.objects.get(queryset_id=queryset_id,hierarchy_id=pr_id,id=shid)#user_ids__contains=tok1['user_id'],
                    surl=sheetdata.datasrc
                except:
                    return Response({'message':'sheet not exists/not valid'},status=status.HTTP_406_NOT_ACCEPTABLE)
                for ch in ast.literal_eval(sheetdata.filter_ids):
                    ch_filter=models.ChartFilters.objects.filter(filter_id=ch).values()
                    ch_list.append(ch_filter)
                flat_filters_data = [item for sublist in ch_list for item in sublist]
                for item in flat_filters_data:
                    if isinstance(item.get("top_bottom"), str):  # Ensure it's a string
                        try:
                            item["top_bottom"] = ast.literal_eval(item["top_bottom"])
                        except (ValueError, SyntaxError):
                            pass
                if surl==None:
                    sheet_data=None
                else:
                    try:
                        data=requests.get(sheetdata.datasrc)
                        sheet_data=data.json() 
                    except:
                        sheet_data=None
                try:
                    shft_query=models.SheetFilter_querysets.objects.get(Sheetqueryset_id=sheetdata.sheet_filt_id)
                except:
                    return Response({'message':'sheetfilter_queryset_id not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                # cl_ro_data=data_reload(sheetdata)
                # if cl_ro_data['status']==200:
                #     reload_data=cl_ro_data['data']
                # else:
                #     return Response({'message':cl_ro_data['message']},status=cl_ro_data['status'])
                d1 = {
                    "sheet_id":sheetdata.id,
                    "sheet_name":sheetdata.sheet_name,
                    "chart_id":sheetdata.chart_id,
                    # "created_by":sheetdata.user_id,
                    "sheet_tag_name":sheetdata.sheet_tag_name,
                    "sheet_data":sheet_data,
                    "created_by":tok1['user_id'],
                    # "sheet_reload_data":reload_data,
                    "sheet_filter_ids":litera_eval(sheetdata.filter_ids),
                    "sheet_filter_quereyset_ids":sheetdata.sheet_filt_id,
                    "datasource_queryset_id":shft_query.datasource_querysetid,
                    "filters_data":flat_filters_data,
                    "custom_query":shft_query.custom_query,
                    "col_data":litera_eval(shft_query.columns),
                    "row_data":litera_eval(shft_query.rows),
                    "pivot_measure":litera_eval(shft_query.pivot_measure),
                    "created_by":sheetdata.user_id,
                }
                return Response(d1,status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
    
###### Remove data from dashboard data file based on sheet id
def remove_sheet_id(data, sheet_id_to_remove):
    # new_data = []
    # for sublist in data:
    #     filtered_sublist = [item for item in sublist if item.get('sheetId') != sheet_id_to_remove]
    #     if filtered_sublist:
    #         new_data.append(filtered_sublist)
    # return new_data

    new_data = []
    for sublist in data:
        # Check if sublist contains dictionaries and filter
        filtered_sublist = [item for item in sublist if isinstance(item, dict) and item.get('sheetId') != sheet_id_to_remove]
        if filtered_sublist:  # Add to new_data only if not empty
            new_data.append(filtered_sublist)
    # print(new_data[0])
    # if isinstance(new_data, list) and len(new_data) == 1 and isinstance(new_data[0], list):
    #     new_data = new_data[0]
    # print(new_data)
    try:
        return new_data[0]
    except:
        return None


def sheet_ds_delete(dsdt,sheet_id,server_id,queryset_id):
    l1=[]
    for i2 in dsdt:
        try:
            o_shid=i2['sheet_ids']  # old sheet ids
            a1=ast.literal_eval(o_shid)
            indx=a1.index(int(sheet_id))
            a1.pop(indx) # new sheet ids after removed
        except:
            a1=i2['sheet_ids']
        try:
            sl_shid=i2['selected_sheet_ids']  # old sheet ids
            sl=ast.literal_eval(sl_shid)
            slindx=sl.index(int(sheet_id))
            sl.pop(slindx) # new sheet ids after removed
        except:
            sl=i2['selected_sheet_ids']

        try:
            dsh_dt=requests.get(i2['datasrc'])
            l1.append(dsh_dt.json())
            resul=remove_sheet_id(l1, sheet_id)
            # print(json.dumps(resul, indent=4))
            if resul==None or resul=='' or resul=="":
                resul1=[]
            else:
                resul1=resul
            dl_key=i2['datapath']
            filesave=file_save_1(resul1,server_id,queryset_id,ip='dashboard',dl_key=dl_key)
            models.dashboard_data.objects.filter(id=i2['id']).update(sheet_ids=a1,selected_sheet_ids=sl,datasrc=filesave['file_url'],datapath=filesave['file_key'])
            dshdt=models.dashboard_data.objects.get(id=i2['id'])
            if dshdt.selected_sheet_ids=='' or dshdt.selected_sheet_ids==None or dshdt.selected_sheet_ids==[]:
                models.dashboard_data.objects.filter(id=i2['id']).delete()
        except:
            pass

def delete_data(query_set_id,server_id,user_id):
    qrst=models.sheet_data.objects.filter(queryset_id=query_set_id).values('id')
    if settings.file_save_path=='s3':
        pass
    else:
        for sheetpath in qrst:
            delete_file(str(sheetpath['datapath']))
    for sheet_id in qrst:
        # dsdt1234=dashboard_data.objects.get(selected_sheet_ids__contains=str(sheet_id))
        # numbers = [num for num in Connections.litera_eval(dsdt1234.selected_sheet_ids) if num != sheet_id]
        # dashboard_data.objects.filter(id=dsdt1234).update(selected_sheet_ids=numbers)
        dsdt=models.dashboard_data.objects.filter(
                Q(sheet_ids__contains=str(sheet_id['id'])) | 
                Q(selected_sheet_ids__contains=str(sheet_id['id'])) | 
                (Q(selected_sheet_ids__contains=str(sheet_id['id'])) & Q(sheet_ids__contains=str(sheet_id['id'])))
            ).values()#user_id=user_id, 
        try:
            sheet_ds_delete(dsdt,sheet_id['id'],server_id,query_set_id)
        except:
            pass
    models.sheet_data.objects.filter(queryset_id=query_set_id).delete()
    models.QuerySets.objects.filter(queryset_id=query_set_id).delete()
    models.calculation_field.objects.filter(queryset_id=query_set_id).delete()
    models.DataSource_querysets.objects.filter(queryset_id=query_set_id).delete()
    models.DataSourceFilter.objects.filter(queryset_id=query_set_id).delete()
    models.SheetFilter_querysets.objects.filter(queryset_id=query_set_id).delete()
    models.ChartFilters.objects.filter(queryset_id=query_set_id).delete()
    models.DashboardFilters.objects.filter(queryset_id=query_set_id).delete()
    models.DashboardFilters.objects.filter(queryset_id=query_set_id).delete()
    # models.Dashboard_drill_through.objects.filter(queryset_id=query_set_id).delete()


@api_view(['DELETE'])
@transaction.atomic
def sheet_delete(request,server_id,queryset_id,sheet_id,token):
    if request.method=='DELETE':
        role_list=roles.get_previlage_id(previlage=[previlages.delete_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if models.sheet_data.objects.filter(id=sheet_id).exists():
                shdt=models.sheet_data.objects.get(id=sheet_id)
            else:
                return Response({'message':'sheet not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
            
            if shdt.is_sample == True:
                return Response({'message':"Sample Dashboard Sheets cannot be deleted"},status=status.HTTP_403_FORBIDDEN)
            
            # dsdt=models.dashboard_data.objects.filter(sheet_ids__contains=str(sheet_id)).values()
            dsdt=models.dashboard_data.objects.filter(
                Q(sheet_ids__contains=str(sheet_id)) | 
                Q(selected_sheet_ids__contains=str(sheet_id)) | 
                (Q(selected_sheet_ids__contains=str(sheet_id)) & Q(sheet_ids__contains=str(sheet_id)))
            ).values()#user_id=user_id, 

            pr_status,server_id2,pr_parameter=columns_extract.parent_id(server_id)
            if pr_status != 200:
                return Response(server_id2,status=pr_status)

            sheet_ds_delete(dsdt,sheet_id,server_id2,queryset_id)
            delete_file(shdt.datapath)
            models.SheetFilter_querysets.objects.filter(Sheetqueryset_id=shdt.sheet_filt_id).delete()
            models.sheet_data.objects.filter(id=sheet_id).delete()
            return Response({'message':'Removed Successfully'},status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        

class sheet_name_update(CreateAPIView):
    serializer_class=serializers.sheet_name_update_serializer

    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_sheet_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                queryset_id=serializer.validated_data['queryset_id']
                server_id=serializer.validated_data['server_id']
                old_sheet_name=serializer.validated_data['old_sheet_name']
                new_sheet_name=serializer.validated_data['new_sheet_name']
                if models.ServerDetails.objects.filter(id=server_id,user_id=tok1['user_id']).exists():
                    pass
                else:
                    return Response({'message':'server id not exists'},status=status.HTTP_404_NOT_FOUND)
                if models.sheet_data.objects.filter(user_id=tok1['user_id'],queryset_id=queryset_id,server_id=server_id,sheet_name=old_sheet_name).exists():
                    models.sheet_data.objects.filter(user_id=tok1['user_id'],queryset_id=queryset_id,server_id=server_id,sheet_name=old_sheet_name).update(sheet_name=new_sheet_name,updated_at=updated_at)
                    return Response({'message':'Sheet name updated successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Sheet not exists'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])


##########    Dashboard data saving,update,delete & Sheet Name update  ##################

def dashboard_s_u(serializer,u_id,ds_id,parameter):
    queryset_id=serializer.validated_data['queryset_id']
    server_id1=serializer.validated_data['server_id']
    data=serializer.validated_data['data']
    sheet_ids=serializer.validated_data['sheet_ids']
    dashboard_tag_name=serializer.validated_data['dashboard_tag_name']
    dashboard_name=serializer.validated_data['dashboard_name']
    # file_id=serializer.validated_data['file_id']
    role_ids=serializer.validated_data['role_ids']
    user_ids=serializer.validated_data['user_ids']
    height=serializer.validated_data['height']
    width=serializer.validated_data['width']
    grid=serializer.validated_data['grid']
    selected_sheet_ids=serializer.validated_data['selected_sheet_ids']
    if models.grid_type.objects.filter(grid_type=str(grid).upper()).exists():
        gr_tb=models.grid_type.objects.get(grid_type=str(grid).upper())
    else:
        return Response({'message':'grid type not exists'},status=status.HTTP_404_NOT_FOUND)
    
    pr_id=server_id1
    server="server"
    queryset="query"
    if parameter=="save":
        if models.dashboard_data.objects.filter(user_id=u_id,dashboard_name=dashboard_name).exists() or models.dashboard_data.objects.filter(dashboard_name=dashboard_name,user_ids__contains=u_id).exists():# and u_id in a:
            return Response({'message':'Dashboard Name already exists, please rename the Dashboard name'},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            dl_key=""
            file_sv=file_save_1(data,server,queryset,ip='dashboard',dl_key=dl_key)
            ds_dt=models.dashboard_data.objects.create(user_id=u_id,sheet_ids=sheet_ids,queryset_id=queryset_id,hierarchy_id=pr_id,role_ids=role_ids,user_ids=user_ids,
                                                datapath=file_sv["file_key"],datasrc=file_sv["file_url"],created_at=created_at,updated_at=updated_at,
                                                dashboard_name=dashboard_name,dashboard_tag_name=dashboard_tag_name,selected_sheet_ids=selected_sheet_ids,
                                                height=height,width=width,grid_id=gr_tb.id)
            models.dashboard_data.objects.filter(id=ds_dt.id).update(created_at=created_at,updated_at=updated_at)
            return Response({'dashboard_id':ds_dt.id,'message':'Saved Successfully'},status=status.HTTP_200_OK)
    elif parameter=="update":
        if models.dashboard_data.objects.filter(user_id=u_id,id=ds_id).exists() or models.dashboard_data.objects.filter(id=ds_id,user_ids__contains=u_id).exists():# and u_id in a:
            old= models.dashboard_data.objects.get(id=ds_id)
            if old.dashboard_name==dashboard_name:
                pass
            else:
                if models.dashboard_data.objects.filter(user_id=u_id,dashboard_name=dashboard_name).exists() or models.dashboard_data.objects.filter(dashboard_name=dashboard_name,user_ids__contains=u_id).exists():# and u_id in a:
                    return Response({'message':'Dashboard Name already exists, please rename the Dashboard name'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass
            file_sv=file_save_1(data,server,queryset,ip='dashboard',dl_key=old.datapath)
            models.dashboard_data.objects.filter(id=ds_id).update(dashboard_name=dashboard_name,selected_sheet_ids=selected_sheet_ids,
            sheet_ids=sheet_ids,datapath=file_sv["file_key"],datasrc=file_sv["file_url"],updated_at=updated_at,dashboard_tag_name=dashboard_tag_name,
            role_ids=role_ids,user_ids=user_ids,height=height,width=width,grid_id=gr_tb.id,queryset_id=queryset_id,hierarchy_id=pr_id)
            models.dashboard_data.objects.filter(id=ds_id).update(updated_at=updated_at)
            return Response({'message':'Updated Successfully'},status=status.HTTP_200_OK)
        else:
            return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
    else:
        pass


class dashboard_image(CreateAPIView):
    serializer_class=serializers.dashboard_image

    @transaction.atomic
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                dashboard_id=serializer.validated_data['dashboard_id']
                imagepath=serializer.validated_data['imagepath']
                if models.dashboard_data.objects.filter(id=dashboard_id).exists(): #,user_id=tok1['user_id']
                    ds_board=models.dashboard_data.objects.get(id=dashboard_id) #,user_id=tok1['user_id']
                    image_sv=image_save_1(imagepath,ip='dashboard/images/',dl_key=ds_board.imagepath)
                    models.dashboard_data.objects.filter(id=dashboard_id).update(updated_at=updated_at,
                                                                                        imagepath=image_sv["file_key"],imagesrc=image_sv["file_url"]) #,user_id=tok1['user_id']
                    return Response({'message':'Updated Successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])



class dahshboard_save(CreateAPIView):
    serializer_class=serializers.dashboard

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_dashboard,previlages.create_dashboard_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                ds_id=""
                sh12 = dashboard_s_u(serializer,tok1['user_id'],ds_id,parameter="save")
                return sh12
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

class dashboard_update(CreateAPIView):
    serializer_class=serializers.dashboard

    @transaction.atomic
    def post(self,request,ds_id,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_dasboard,previlages.edit_dashboard_title,previlages.view_dashboard,previlages.view_dashboard_filter])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if models.dashboard_data.objects.filter(id=ds_id).exists():
                dashboarddata=models.dashboard_data.objects.get(id=ds_id)
            else:
                return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            # a=[item for sublist in ast.literal_eval(dashboarddata.user_ids) for item in sublist]
            if models.dashboard_data.objects.filter(id=ds_id,user_id=str(tok1['user_id'])).exists() or models.dashboard_data.objects.filter(id=ds_id,user_ids__contains=tok1['user_id']):# and tok1['user_id'] in a:
                pass
            else:
                return Response({'message':'User Not assigned to this ROLE/Not Assigned'},status=status.HTTP_401_UNAUTHORIZED)
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                sh12 = dashboard_s_u(serializer,tok1['user_id'],ds_id,parameter="update")
                return sh12
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        


class dashboard_retrieve(CreateAPIView):
    serializer_class=serializers.dashboard_retrieve_serializer

    @transaction.atomic
    def post(self,request,token=None):
        if token==None:
            tok_status=200
        else:
            role_list=roles.get_previlage_id(previlage=[previlages.view_dashboard,previlages.view_dashboard_filter])
            tok1 = roles.role_status(token,role_list)
            tok_status=tok1['status']

        if tok_status==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                dashboard_id=serializer.validated_data['dashboard_id']
                if models.dashboard_data.objects.filter(id=dashboard_id).exists():
                    dashboarddata=models.dashboard_data.objects.get(id=dashboard_id)
                    durl=dashboarddata.datasrc
                    gr_tb=models.grid_type.objects.get(id=dashboarddata.grid_id)
                    if dashboarddata.is_public==True and token==None:
                        user_id=dashboarddata.user_id
                    elif dashboarddata.is_public==False and token==None:
                        return Response({'message':'access token in needed'},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        user_id=tok1['user_id']   
                else:
                    return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
                # a=[item for sublist in ast.literal_eval(dashboarddata.user_ids) for item in sublist]
                if models.dashboard_data.objects.filter(id=dashboard_id,user_id=str(user_id)).exists() or models.dashboard_data.objects.filter(id=dashboard_id,user_ids__contains=user_id):# and tok1['user_id'] in a:
                    pass
                else:
                    return Response({'message':'User Not assigned to this ROLE/Not Assigned'},status=status.HTTP_401_UNAUTHORIZED)
                sheet_name=[]
                # sheets_data=[]
                if dashboarddata.sheet_ids==[] or dashboarddata.sheet_ids==None or dashboarddata.sheet_ids=='':
                    # sheets_data=[]
                    sheet_name=[]
                else:
                    for shid in ast.literal_eval(dashboarddata.sheet_ids):
                        try:
                            shdt=models.sheet_data.objects.get(id=shid)
                            sheet_name.append(shdt.sheet_name)
                        except:
                            sh_ids = litera_eval(dashboarddata.sheet_ids)
                            selected_sh_ids = litera_eval(dashboarddata.selected_sheet_ids)
                            updated = False
                            if shid in sh_ids:
                                sh_ids.remove(shid)
                                updated = True
                            if shid in selected_sh_ids:
                                selected_sh_ids.remove(shid)
                                updated = True
                            if updated:
                                models.dashboard_data.objects.filter(id=dashboard_id).update(
                                    sheet_ids=sh_ids,
                                    selected_sheet_ids=selected_sh_ids
                                )
                            else:
                                return Response({'message': 'Sheet {} does not exist'.format(shid)}, status=status.HTTP_404_NOT_FOUND)
                if durl==None:
                    dashboard_data=None
                else:
                    try:
                        data=requests.get(dashboarddata.datasrc)
                        dashboard_data=data.json() 
                    except:
                        dashboard_data=None
                role_ids = litera_eval(dashboarddata.role_ids)
                user_ids = litera_eval(dashboarddata.user_ids)
                if role_ids=="" or role_ids=='':
                    role_ids=[]
                if user_ids=="" or user_ids=='':
                    user_ids=[]
                d1 = {
                    "dashboard_id":dashboarddata.id,
                    "is_public":dashboarddata.is_public,
                    "is_sample" : dashboarddata.is_sample,
                    "dashboard_name":dashboarddata.dashboard_name,
                    "dashboard_tag_name":dashboarddata.dashboard_tag_name,
                    "sheet_ids":litera_eval(dashboarddata.sheet_ids),
                    "selected_sheet_ids":litera_eval(dashboarddata.selected_sheet_ids),
                    "sheet_names":sheet_name,
                    "grid_type":gr_tb.grid_type,
                    "height":dashboarddata.height,
                    "width":dashboarddata.width,
                    "hierarchy_id":litera_eval(dashboarddata.hierarchy_id),
                    # "server_id":litera_eval(dashboarddata.server_id),
                    "queryset_id":litera_eval(dashboarddata.queryset_id),
                    # "file_id":litera_eval(dashboarddata.file_id),
                    "dashboard_image":dashboarddata.imagesrc,
                    "dashboard_data":dashboard_data,
                    # "sheet_reload_data":sheets_data,
                    "role_ids":role_ids,
                    "user_ids":user_ids
                }
                return Response(d1,status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
    

@api_view(['DELETE'])
@transaction.atomic
def dashboard_delete(request,dashboard_id,token):
    if request.method=='DELETE':
        role_list=roles.get_previlage_id(previlage=[previlages.delete_dashboard])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if models.dashboard_data.objects.filter(id=dashboard_id).exists():
                dashboarddata=models.dashboard_data.objects.get(id=dashboard_id)
            else:
                return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            
            if dashboarddata.is_sample == True:
                return Response({'message':"Sample Dashboard cannot be deleted"},status=status.HTTP_403_FORBIDDEN)
            # a=[item for sublist in ast.literal_eval(dashboarddata.user_ids) for item in sublist]
            if models.dashboard_data.objects.filter(id=dashboard_id,user_id=str(tok1['user_id'])).exists() or models.dashboard_data.objects.filter(id=dashboard_id,user_ids__contains=tok1['user_id']):# and tok1['user_id'] in a:
                pass
            else:
                return Response({'message':'User Not assigned to this ROLE/Not Assigned'},status=status.HTTP_401_UNAUTHORIZED)
            
            delete_file(dashboarddata.datapath)
            delete_file(dashboarddata.imagepath)
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(dashboarddata.datapath))
            models.dashboard_data.objects.filter(id=dashboard_id).delete()
            return Response({'message':'Removed Successfully'},status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'method':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        

class dashboard_name_update(CreateAPIView):
    serializer_class=serializers.dashboard_name_update_serializer

    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_dashboard_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                queryset_id=serializer.validated_data['queryset_id']
                server_id=serializer.validated_data['server_id']
                old_dashboard_name=serializer.validated_data['old_dashboard_name']
                new_dashboard_name=serializer.validated_data['new_dashboard_name']
                if models.ServerDetails.objects.filter(id=server_id,user_id=tok1['user_id']).exists():
                    pass
                else:
                    return Response({'message':'server id not exists'},status=status.HTTP_404_NOT_FOUND)
                if models.dashboard_data.objects.filter(user_id=tok1['user_id'],queryset_id=queryset_id,server_id=server_id,dashboard_name=old_dashboard_name).exists():
                    models.dashboard_data.objects.filter(user_id=tok1['user_id'],queryset_id=queryset_id,server_id=server_id,dashboard_name=old_dashboard_name).update(dashboard_name=new_dashboard_name,updated_at=updated_at)
                    return Response({'message':'Dashboard name updated successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer not valid'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

def display_name(hierarchy_id):
    try:
        status1,parameter,server_id,file_id,quickbooks_id,salesforce_id,halops_id,connectwise_id,shopify_id,google_sheet_id,pr_id=columns_extract.ids_final_status(hierarchy_id)
        if status1 != 200:
            return Response({'message':'Invalid Id'},status=status1)
    except Exception as e:
        models.QuerySets.objects.filter(hierarchy_id=hierarchy_id).delete()
        models.sheet_data.objects.filter(hierarchy_id=hierarchy_id).delete()
    
    if (file_id is not None or file_id!='') and parameter=='files':
        try:
            ser_db_data=models.FileDetails.objects.get(id=file_id)
        except:
            return Response({'message':'file_details_id/file_type not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (server_id is not None or server_id!='') and parameter=='server':
        try:
            ser_db_data=models.ServerDetails.objects.get(id=server_id,is_connected=True)
        except:
            return Response({'message':'server_details_id/server_type not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (quickbooks_id is not None or quickbooks_id!='') and parameter=='quickbooks':
        try:
            ser_db_data=qb_models.TokenStoring.objects.get(qbuserid=quickbooks_id)
        except:
            return Response({'message':'quickbooks id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (salesforce_id is not None or salesforce_id!='') and parameter=='salesforce':
        try:
            ser_db_data=qb_models.TokenStoring.objects.get(salesuserid=salesforce_id)
        except:
            return Response({'message':'salesforce id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (halops_id is not None or halops_id!='') and parameter=='halops':
        try:
            ser_db_data=qb_models.HaloPs.objects.get(id=halops_id)
        except:
            return Response({'message':'halops id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (connectwise_id is not None or connectwise_id!='') and parameter=='connectwise':
        try:
            ser_db_data=qb_models.connectwise.objects.get(id=connectwise_id)
        except:
            return Response({'message':'connectwise id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (shopify_id is not None or shopify_id!='') and parameter=='shopify':
        try:
            ser_db_data=qb_models.Shopify.objects.get(id=shopify_id)
        except:
            return Response({'message':'shopify id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif (google_sheet_id is not None or google_sheet_id!='') and parameter=='google_sheets':
        try:
            ser_db_data=qb_models.TokenStoring.objects.get(id=google_sheet_id)
        except:
            return Response({'message':'googhe sheet id not exists'},status=status.HTTP_404_NOT_FOUND)
    elif parameter=='cross_database':
        ser_db_data=None
    else:
        pass
    if parameter=='server':
        parameter=models.ServerType.objects.get(id=ser_db_data.server_type).server_type.lower()
    else:
        parameter=parameter

    return ser_db_data,parameter


def charts_dt(charts,tok1,database_name):
    cl_list=[]
    for ch in charts:
        try:
            dis_name,para=display_name(ch['hierarchy_id'])
            database_name=dis_name.display_name
        except:
            return Response({'message':'Invalid Id'},status=status.HTTP_404_NOT_FOUND)
        chid=models.charts.objects.get(id=ch['chart_id'])
        if chid.chart_type=="HIGHLIGHT_TABLES" or chid.chart_type=="Table":
            sheet_type="Table"
        elif chid.chart_type=='PIVOT':
            sheet_type="PIVOT"
        else:
            sheet_type="Chart"
        created_by = "Example" if ch['is_sample'] else tok1['username']  # Update created_by based on is_sample
        query_id = ch['queryset_id']
        try:
            qrtb12=models.QuerySets.objects.get(queryset_id=ch['queryset_id'])
        except:
            return Response({'message':'queryset_id: {} not exist'.format(query_id)},status=status.HTTP_404_NOT_FOUND)
        data = {
            "database_name":database_name,
            "created_by":created_by,
            "sheet_type":sheet_type,
            "chart":chid.chart_type,
            "chart_id":chid.id,
            "is_sample": ch["is_sample"],
            "sheet_id":ch['id'],
            "sheet_tag_name":ch['sheet_tag_name'],
            "sheet_name":ch['sheet_name'],
            # "server_id":ch['server_id'],
            # "file_id":ch['file_id'],
            'hierarchy_id':ch['hierarchy_id'],
            "queryset_id":ch['queryset_id'],
            "created":ch['created_at'].date(),
            "Modified":ch['updated_at'].date(),
            # "queryset_name":qrtb12.query_name,
            # "sheet_data":durl.json(),
            # "sheet_reload_data":reload_data
        }
        data['queryset_name']=qrtb12.query_name
        cl_list.append(data)
    result={
        "status":200,
        "database_name":database_name,
        "sheets":cl_list
    }
    return result


def remove_duplicate_dashboards(data):
    seen_ids = set()
    unique_dashboards = []
    for sheet in data:
        if sheet['dashboard_id'] not in seen_ids:
            seen_ids.add(sheet['dashboard_id'])
            unique_dashboards.append(sheet)
    data = unique_dashboards
    return data


def dashboard_dt(charts,tok1):
    cl_list=[]
    sample_dashboards = [] 
    for ch in charts:
        gr_tb=models.grid_type.objects.get(id=ch['grid_id'])
        created_by = "Example" if ch['is_sample'] else tok1['username']  # Updated created_by based on is_sample
        data = {
            "created_by":created_by,
            "sheet_ids":litera_eval(ch['sheet_ids']),
            "dashboard_id":ch['id'],
            "is_public":ch['is_public'],
            "is_sample": ch["is_sample"],
            "dashboard_name":ch['dashboard_name'],
            "dashboard_tag_name":ch['dashboard_tag_name'],
            "selected_sheet_ids":litera_eval(ch['selected_sheet_ids']),
            "grid_type":gr_tb.grid_type,
            "height":ch['height'],
            "width":ch['width'],
            "hierarchy_id":litera_eval(ch['hierarchy_id']),
            "queryset_id":litera_eval(ch['queryset_id']),
            "dashboard_image":ch['imagesrc'],
            "database_name":None,
            "created":ch['created_at'].date(),
            "Modified":ch['updated_at'].date(),
        }
        if ch['is_sample']:  # Check if it's a sample dashboard
            sample_dashboards.append(data)
        else:
            cl_list.append(data)
            
    fn_data=remove_duplicate_dashboards(cl_list)
    return fn_data, sample_dashboards


def query_sets(qrsets,tok1):
    qrsets_l=[]
    for qr in qrsets:
        try:
            ser_dt,para=display_name(qr['hierarchy_id'])
        except:
            dat1 = {
                'message':'Invalid Hierarchy Id',
                'status':401
            }
            return dat1
        qrsets_filter=[]
        filter_ids=models.DataSource_querysets.objects.filter(queryset_id=qr['queryset_id']).values().order_by('-updated_at')
        qrsets_filter.append(dt for dt in filter_ids)
        created_by = "Example" if qr['is_sample'] else tok1['username']
        data = {
            "database_name":ser_dt.display_name,
            "queryset_id":qr['queryset_id'],
            "created_by":created_by,
            "queryset_name":qr['query_name'],
            "hierarchy_id":qr['hierarchy_id'],
            "is_custom_sql":qr['is_custom_sql'],
            "custom_query":qr['custom_query'],
            "created":qr['created_at'].date(),
            "modified":qr['updated_at'].date(),
            "datasource_filterdata":[item for sublist in qrsets_filter for item in sublist]
        }
        qrsets_l.append(data)
    return qrsets_l
    

def pagination(request,data,page_no,page_count):
    try:	
        paginator = Paginator(data,page_count)
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
    except Exception as e:
        data1 = {
            "status":400,
            "data":"Data not exists in page/Un supported page number"
        }
    return data1

## user all sheets based on quersetid,serverid, else all
class charts_fetch(CreateAPIView):
    serializer_class=serializers.charts_fetch_qr

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                queryset_id = serializer.validated_data['queryset_id']
                server_id1 = serializer.validated_data['server_id']
                search = serializer.validated_data['search']
                # file_id = serializer.validated_data['file_id']
                if queryset_id=='' and server_id1=='':
                    return Response({'message':'queryset_id, server_id fields are required'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass

                pr_id=server_id1
                try:
                    ser_db_data,para=display_name(server_id1)
                    dis_name=ser_db_data.display_name
                except:
                    return Response({'message':'Invalid Id'},status=status.HTTP_404_NOT_FOUND)
                    
                if models.QuerySets.objects.filter(user_id=tok1['user_id'],hierarchy_id=pr_id,queryset_id=queryset_id).exists():
                    pass
                else:
                    return Response({'message':'queryset id not exists'},status=status.HTTP_404_NOT_FOUND)
                    
                if search=='':
                    charts = models.sheet_data.objects.filter(user_id=tok1['user_id'],hierarchy_id=pr_id,queryset_id=queryset_id).values().order_by('updated_at')
                else:
                    charts = models.sheet_data.objects.filter(user_id=tok1['user_id'],hierarchy_id=pr_id,queryset_id=queryset_id,sheet_name__icontains=search).values().order_by('updated_at')
                
                sheets_list=[]
                for sh in charts:
                    shdt=models.sheet_data.objects.get(id=sh['id'])
                    try:
                        durl=requests.get(shdt.datasrc)
                        durl_data=durl.json()
                    except:
                        durl_data=None
                    # cl_ro_data=data_reload(shdt)
                    # if cl_ro_data['status']==200:
                    #     reload_data=cl_ro_data['data']
                    # else:
                    #     return Response({'message':cl_ro_data['message']},status=cl_ro_data['status'])
                    charts12=models.sheet_data.objects.filter(id=sh['id']).values().order_by('-updated_at')
                    charts_data=charts_dt(charts12,tok1,ser_db_data.display_name)
                    try:
                        charts_data['status']==200
                    except:
                        return charts_data
                    charts_data['sheets'][0]['sheet_data']=durl_data
                    # charts_data['sheets'][0]['sheet_reload_data']=reload_data
                    sheets_list.append(charts_data['sheets'])
                return Response([item for sublist in sheets_list for item in sublist],status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
 

    def get(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            charts = models.sheet_data.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
            server_id=''
            file_id=''
            # charts_data=charts_dt(charts,tok1,server_id=server_id,file_id=file_id)
            data = []
            for chts in charts:
                data.append({'sheet_id':chts['id'],'sheet_list_name':chts['sheet_name'],'queryset_id':chts['queryset_id']})
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
        

    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                search = serializer.validated_data['search']
                page_no = serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                if search=='':
                    charts = models.sheet_data.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
                else:
                    charts = models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).values().order_by('-updated_at')
                display_name=''
                charts_data=charts_dt(charts,tok1,display_name)
                try:
                    charts_data['status']==200
                except:
                    return charts_data
                try:
                    resul_data=pagination(request,charts_data['sheets'],page_no,page_count)
                    if not resul_data['status']==200:
                        return resul_data
                    resul_data["database_name"]=charts_data['database_name']
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({'message':'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])


## user all dashboards based on quersetid,serverid, else all
class dashboard_fetch(CreateAPIView):
    serializer_class=serializers.charts_fetch_qr

    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_dashboard])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                queryset_id = serializer.validated_data['queryset_id']
                server_id1 = serializer.validated_data['server_id']
                search = serializer.validated_data['search']
                try:
                    ser_dt,para=display_name(server_id1)
                    display_name=ser_dt.display_name
                except:
                    dat1 = {
                        'message':'Invalid Hierarchy Id',
                        'status':401
                    }
                    return Response(dat1,status=status.HTTP_401_UNAUTHORIZED)
                if queryset_id=='' and server_id1==None:
                    return Response({'message':'queryset_id and hierarchy_id fields are required'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass
                if search=='':
                    charts = models.dashboard_data.objects.filter(
                                        Q(user_id=tok1['user_id']) | Q(user_ids__contains=[tok1['user_id']]),
                                        hierarchy_id__contains=server_id1,
                                        queryset_id__contains=queryset_id
                                    ).values().order_by('-updated_at')
                else:
                    charts = models.dashboard_data.objects.filter(
                                        Q(user_id=tok1['user_id']) | Q(user_ids__contains=[tok1['user_id']]),
                                        hierarchy_id__contains=server_id1,
                                        queryset_id__contains=queryset_id,
                                        dashboard_name__icontains=search
                                    ).values().order_by('-updated_at')
                dashboards_data,_=dashboard_dt(charts,tok1)
                return Response(dashboards_data,status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

    def get(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            charts = models.dashboard_data.objects.filter(
                                        Q(user_id=tok1['user_id']) | Q(user_ids__contains=[tok1['user_id']]),
                                    ).values().order_by('-updated_at')
            dashboards_data,_=dashboard_dt(charts,tok1)
            return Response(dashboards_data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
        

    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                search = serializer.validated_data['search']
                page_no = serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                if search=='':
                    charts = models.dashboard_data.objects.filter(
                                        Q(user_id=tok1['user_id']) | Q(user_ids__contains=[tok1['user_id']]),
                                    ).values().order_by('-updated_at')
                else:
                    charts = models.dashboard_data.objects.filter(
                                            Q(user_id=tok1['user_id']) | Q(user_ids__contains=[tok1['user_id']]),
                                            dashboard_name__icontains=search
                                        ).values().order_by('-updated_at')
                charts_data, sample_dashboards = dashboard_dt(charts,tok1)
                try:
                    resul_data=pagination(request,charts_data,page_no,page_count)
                    if not resul_data['status']==200:
                        return resul_data
                    resul_data["sample_dashboards"] = sample_dashboards  # Added sample dashboards to response
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({{'message':'Empty page/data not exists/selected count of records are not exists'}},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'data not exists with the page'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
            


##### dashboard property update
class dashboard_property_update(CreateAPIView):
    serializer_class=serializers.dash_prop_update

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.edit_dashboard_filter,previlages.edit_dashboard_title,previlages.edit_dasboard])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                dashboard_id = serializer.validated_data['dashboard_id']
                role_ids = serializer.validated_data['role_ids']
                user_ids = serializer.validated_data['user_ids']
                if models.dashboard_data.objects.filter(id=dashboard_id).exists():
                    role_1=litera_eval(str(role_ids))
                    user_1=litera_eval(str(user_ids))
                    models.dashboard_data.objects.filter(id=dashboard_id).update(role_ids=role_1,user_ids=user_1)
                    dshb_dt=models.dashboard_data.objects.get(id=dashboard_id)
                    for sh in litera_eval(dshb_dt.sheet_ids):
                        shdt=models.sheet_data.objects.get(id=sh)
                        ## get the existing user_ids and append the new user_id
                        ex_shids=shdt.user_ids
                        if ex_shids==None or ex_shids=='' or ex_shids==[]:
                            ne_shids=user_ids
                        else:
                            ne_shids=litera_eval(ex_shids).extend(user_ids)
                        models.sheet_data.objects.filter(id=sh).update(user_ids=ne_shids)
                    return Response({'message':'Dashboard Shared successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])




##### List of user sheet names (only sheet names)
class user_list_names(CreateAPIView):
    serializer_class=serializers.charts_fetch_qr

    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                queryset_id = serializer.validated_data['queryset_id']
                server_id1 = serializer.validated_data['server_id']
                sheet_list=[]
                status1,tb_id,parameter=columns_extract.parent_id(server_id1)
                if status1 != 200:
                    return Response({'message':'Invalid Id'},status=status1)
                sheet_dt=models.sheet_data.objects.filter(hierarchy_id=server_id1,queryset_id=queryset_id).values('id','sheet_name').order_by('id')  ##,user_id=tok1['user_id']
                # sheet_dt2=models.sheet_data.objects.filter(server_id=server_id,queryset_id=queryset_id).values('id','sheet_name') ##,user_ids__contains=tok1['user_id']
                for sh in sheet_dt:
                    sheet_list.append({'id':sh['id'],'sheet_name':sh['sheet_name']})
                return Response({'data':sheet_list},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])   
        

def charts_select(charts,u_id):
    ch_list=[]
    for ch in charts:
        data = {
            "created_by":u_id,
            "sheet_id":ch['id'],
            "sheet_name":ch['sheet_name'],
            # "server_id":ch['server_id'],
            # "file_id":ch['file_id'],
            "hierarchy_id":ch['hierarchy_id'],
            "queryset_id":ch['queryset_id'],
            "created":ch['created_at'].date(),
            "Modified":ch['updated_at'].date(),
            "is_selected":False,
            "created_by":ch['user_id']
        }
        ch_list.append(data)
    return ch_list



def query_sheet_search(qrse,tok1,sheet_ids):
    final_list=[]
    for qr in qrse:
        try:
            ser_dt,para=display_name(qr['hierarchy_id'])
            db_name=ser_dt.display_name
        except:
            dat1 = {
                'message':'Invalid Hierarchy Id',
                'status':401
            }
            return dat1
        if para.lower()=='files':
            created=ser_dt.uploaded_at.date()
            updated=ser_dt.updated_at.date()
        else:
            created=ser_dt.created_at.date()
            updated=ser_dt.updated_at.date()

        sheet_data={}
        created_by = "Example" if qr['is_sample'] else tok1['username']  # Update created_by based on is_sample
        
        shtdt=models.sheet_data.objects.filter(queryset_id=qr['queryset_id']).values().order_by('-updated_at')
        sheet_data['queryset_id']=qr['queryset_id']
        sheet_data['queryset_name']=qr['query_name']
        sheet_data['hierarchy_id']=qr['hierarchy_id'],
        sheet_data['database_name']=ser_dt.display_name,
        sheet_data['created_by']=created_by
        sheet_data['created_at']=created
        sheet_data['modified_at']=updated
        sheet_data['is_selected']=False
        sheet_data['sheet_selected']=False
        charts_dt=charts_select(shtdt,created_by)
        sheet_data['sheet_data']=charts_dt
        final_list.append(sheet_data)
    for queryset in final_list:
        for sheet in queryset['sheet_data']:
            if sheet['sheet_id'] in sheet_ids:
                sheet['is_selected'] = True
        if all(sheet['is_selected'] for sheet in queryset['sheet_data']):
            queryset['is_selected'] = True
        if any(sheet['is_selected'] for sheet in queryset['sheet_data']):
            queryset['sheet_selected'] = True
    try:
        data = {
            "status":200,
            "data":final_list
        }
        return data
    except:
        data = {
            "status":400,
            "message":'Empty page/data not exists/selected count of records are not exists'
        }
        return data
    

class user_sheets_list_data(CreateAPIView):
    serializer_class=serializers.sheets_list_seri

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_sheet,previlages.view_sheet_filters,previlages.view_dashboard,previlages.view_dashboard_filter,
                                                    previlages.edit_dasboard,previlages.edit_sheet,previlages.edit_sheet_title,previlages.edit_dashboard_filter,
                                                    previlages.edit_dashboard_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                sheet_ids=serializer.validated_data['sheet_ids']
                search=serializer.validated_data['search']
                page_no=serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                if sheet_ids=='' or sheet_ids==None:
                    sheet_ids=[]
                else:
                    sheet_ids=sheet_ids
                if search=='' or search==None:
                    qrse=models.QuerySets.objects.filter(user_id=tok1['user_id']).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at')
                elif models.QuerySets.objects.filter(user_id=tok1['user_id'],query_name__icontains=search).exists():
                    qrse=models.QuerySets.objects.filter(user_id=tok1['user_id'],query_name__icontains=search).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at')
                elif models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).exists():
                    sheet_dt=models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).values().order_by('-updated_at')
                    querysets_li=[qrl['queryset_id'] for qrl in sheet_dt]
                    final_list=[]
                    for qrs in querysets_li:
                        qrse=models.QuerySets.objects.filter(queryset_id=qrs).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at')
                        sheets_data = query_sheet_search(qrse,tok1,sheet_ids)
                        if sheets_data['status']==200:
                            sheets_data['data'] = [sheet for sheet in sheets_data['data'] if sheet['sheet_data']]
                            final_list.append(sheets_data['data'])
                        else:
                            return Response({'message':sheets_data['message']},status=sheets_data['status'])
                    try:
                        resul_data=pagination(request,[item for sublist in final_list for item in sublist],page_no,page_count)
                        if not resul_data['status']==200:
                            return resul_data
                        return Response(resul_data,status=status.HTTP_200_OK)
                    except:
                        return Response({"message":'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)
                # elif models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).exists() and models.QuerySets.objects.filter(user_id=tok1['user_id'],query_name__icontains=search).exists():
                #     qrse=models.QuerySets.objects.filter(user_id=tok1['user_id'],query_name__icontains=search).values().order_by('-updated_at')
                #     sheet_dt=models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).values().order_by('-updated_at')
            
                else:
                    return Response([],status=status.HTTP_404_NOT_FOUND)

                sheets_data = query_sheet_search(qrse,tok1,sheet_ids)
                if sheets_data['status']==200:
                    try:
                        sheets_data['data'] = [sheet for sheet in sheets_data['data'] if sheet['sheet_data']]
                        resul_data=pagination(request,sheets_data['data'],page_no,page_count)
                        if not resul_data['status']==200:
                            return resul_data
                        return Response(resul_data,status=status.HTTP_200_OK)
                    except:
                        return Response({"message":'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message':sheets_data['message']},status=sheets_data['status'])
        else:
            return Response(tok1,status=tok1['status'])
    


class sheet_lists_data(CreateAPIView):
    serializer_class=serializers.sheets_list_serializer

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.view_sheet,previlages.view_sheet_filters,previlages.view_dashboard,previlages.view_dashboard_filter,
                                                    previlages.edit_dasboard,previlages.edit_sheet,previlages.edit_sheet_title,previlages.edit_dashboard_filter,
                                                    previlages.edit_dashboard_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                sheet_ids=serializer.validated_data['sheet_ids']
                sheets_list=[]
                for sh in sheet_ids:
                    if models.sheet_data.objects.filter(id=sh).exists():
                        pass
                    else:
                        return Response({'message':'sheet {} not exists'.format(sh)},status=status.HTTP_404_NOT_FOUND)
                    charts=models.sheet_data.objects.filter(id=sh).values().order_by('-updated_at')
                    shdt=models.sheet_data.objects.get(id=sh)
                    try:
                        durl=requests.get(shdt.datasrc)
                        durl_data=durl.json()
                    except:
                        durl_data=None
                    status1,tb_id,parameter=columns_extract.parent_id(shdt.hierarchy_id)
                    if status1 != 200:
                        return Response({'message':'Invalid Id'},status=status1)
                    display_name=''
                    charts_data=charts_dt(charts,tok1,display_name)
                    try:
                        charts_data['status']==200
                    except:
                        return charts_data
                    charts_data['sheets'][0]['sheet_data']=durl_data
                    charts_data['sheets'][0]['created_by']=shdt.user_id
                    # charts_data['sheets'][0]['sheet_reload_data']=reload_data
                    sheets_list.append(charts_data)
                return Response(sheets_list,status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
            


@api_view(['GET'])
@transaction.atomic
def dashboard_data_previlages(request,dashboard_id,token):
    if request.method=='GET':
        role_list=roles.get_previlage_id(previlage=[previlages.view_dashboard,
                                                    previlages.edit_dasboard,previlages.edit_dashboard_filter,
                                                    previlages.edit_dashboard_title])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            if models.dashboard_data.objects.filter(id=dashboard_id,user_id=tok1['user_id']).values().exists():
                dash_dt=models.dashboard_data.objects.get(id=dashboard_id,user_id=tok1['user_id'])
                roles_li=[]
                users_li=[]
                role_ids=litera_eval(dash_dt.role_ids)
                user_ids=litera_eval(dash_dt.user_ids)
                if role_ids!=None and user_ids!=None:
                    pass
                else:
                    return Response({'roles':[],'users':[]}, status=status.HTTP_200_OK)
                for rl,us in zip_longest(role_ids, user_ids, fillvalue=None):
                    if rl!=None:
                        rl_tb=models.Role.objects.get(role_id=rl)
                        id1=rl_tb.role_id
                        rlname=rl_tb.role
                    else:
                        id1=None
                        rlname=None
                    if us!=None:
                        us_tb=models.UserProfile.objects.get(id=us)
                        usid=us_tb.id
                        usname=us_tb.username
                    else:
                        usid=None
                        usname=None
                    roles_li.append({'id':id1,'role':rlname})
                    users_li.append({'user_id':usid,'username':usname})
                return Response({'roles':roles_li,'users':users_li}, status=status.HTTP_200_OK)
            else:
                return Response({'message':'Dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


class sheets_update_dashboard(CreateAPIView):
    serializer_class=serializers.dashboard_sheet_update

    @transaction.atomic
    def put(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_dashboard,previlages.view_dashboard,previlages.create_sheet,previlages.view_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                sheet_ids=serializer.validated_data['sheet_ids']
                dashboard_id=serializer.validated_data['dashboard_id']
                if models.dashboard_data.objects.filter(id=dashboard_id).values().exists():   ####,user_id=tok1['user_id']
                    dshb_dt=models.dashboard_data.objects.get(id=dashboard_id)  ##,user_id=tok1['user_id']
                    ex_sh_ids=litera_eval(dshb_dt.selected_sheet_ids)
                    if ex_sh_ids==[] or ex_sh_ids=="":
                        models.dashboard_data.objects.filter(id=dashboard_id).update(selected_sheet_ids=list(set(sheet_ids)))  ##,user_id=tok1['user_id']
                    else:
                        for shid in sheet_ids:
                            ex_sh_ids.append(shid)
                        models.dashboard_data.objects.filter(id=dashboard_id).update(selected_sheet_ids=list(set(ex_sh_ids))) ##,user_id=tok1['user_id']
                    return Response({'message':'updated successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Dashboard not exists'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])




class query_based_sheets(CreateAPIView):
    serializer_class=serializers.queryset_id_sheets

    @transaction.atomic
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_dashboard,previlages.view_dashboard,previlages.create_sheet,previlages.view_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                queryset_id=serializer.validated_data['queryset_id']
                search=serializer.validated_data['search']
                page_no=serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                if queryset_id==None or queryset_id=='' or queryset_id=='':
                    if search=='' or search==None or search=="":
                        charts=models.sheet_data.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
                    else:
                        charts=models.sheet_data.objects.filter(user_id=tok1['user_id'],sheet_name__icontains=search).values().order_by('-updated_at')
                else:
                    if search=='' or search==None or search=="":
                        charts=models.sheet_data.objects.filter(queryset_id=queryset_id,user_id=tok1['user_id']).values().order_by('-updated_at')
                    else:
                        charts=models.sheet_data.objects.filter(queryset_id=queryset_id,user_id=tok1['user_id'],sheet_name__icontains=search).values().order_by('-updated_at')
                disp_name=''
                charts_data=charts_dt(charts,tok1,disp_name)
                try:
                    charts_data['status']==200
                except:
                    return charts_data
                try:
                    resul_data=pagination(request,charts_data['sheets'],page_no,page_count)
                    if not resul_data['status']==200:
                        return resul_data
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({'message':'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
            


@api_view(['GET'])
@transaction.atomic
def queryset_list(request,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qrsets=models.QuerySets.objects.filter(user_id=tok1['user_id']).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at')
            data = []
            for qr in qrsets:
                try:
                    dsqr_data=models.DataSource_querysets.objects.get(queryset_id=qr['queryset_id'])
                    dsqr_id=dsqr_data.datasource_querysetid
                except:
                    dsqr_id=None
                data.append({'id':qr['queryset_id'],'queryset_name':qr['query_name'],'hierarchy_id':qr['hierarchy_id'],'datasource_queryset_id':dsqr_id})
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)

        
class saved_queries(CreateAPIView):
    serializer_class=serializers.SearchFilterSerializer

    def get(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qrsets=models.QuerySets.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')  #,is_custom_sql=True
            try:
                queryset=query_sets(qrsets,tok1)
            except:
                return Response({'message':'Invalid Id'},status=status.HTTP_404_NOT_FOUND)
            return Response(queryset,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])

    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                search=serializer.validated_data['search']
                page_no=serializer.validated_data['page_no']
                page_count = serializer.validated_data['page_count']
                if search=='':
                    qrsets=models.QuerySets.objects.filter(user_id=tok1['user_id']).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at') #,is_custom_sql=True
                else:
                    qrsets=models.QuerySets.objects.filter(user_id=tok1['user_id'],query_name__icontains=search).exclude(query_name__isnull=True).exclude(query_name=None).exclude(query_name='').values().order_by('-updated_at') #is_custom_sql=True,
                try:
                    queryset=query_sets(qrsets,tok1)
                except:
                    return Response({'message':'Invalid hierarchy_Id'},status=status.HTTP_404_NOT_FOUND)
                try:
                    resul_data=pagination(request,queryset,page_no,page_count)
                    if not resul_data['status']==200:
                        return resul_data
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({{'message':'Empty page/data not exists/selected count of records are not exists'}},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])

        


##########################################################################################################################
class Multicolumndata(CreateAPIView):
    serializer_class = serializers.GetTableInputSerializer
    
    @transaction.atomic()
    def post(self, request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                db_id = serializer.validated_data['database_id']
                table_data = serializer.validated_data['table_1']
                try:
                    sd = ServerDetails.objects.get(id=db_id)
                except ServerDetails.DoesNotExist:
                    return Response({"message": "ServerDetails with the given ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
                try:
                    st = ServerType.objects.get(id=sd.server_type)
                except ServerType.DoesNotExist:
                    return Response({"message": "ServerType with the given ID does not exist."}, status=status.HTTP_404_NOT_FOUND)

                # server_conn=columns_extract.server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,st.server_type.upper(),sd.database_path)
                # if server_conn['status']==200:
                #     engine=server_conn['engine']
                #     cursor=server_conn['cursor']
                # else:
                #     return Response(server_conn,status=server_conn['status'])
                try:
                    clickhouse_class = clickhouse.Clickhouse(sd.display_name)
                    engine=clickhouse_class.engine
                    cursor=clickhouse_class.cursor
                except:
                    return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)

                response_col_data = {}
                for key, col_list in table_data.items():
                    for col in col_list:
                        query = text(f"SELECT {col} FROM {key}")
                        data = cursor.execute(query)
                        column_data = [row[0] for row in data]
                        key_col = f'{key}.{col}'
                        data_type = np.array(column_data).dtype
                        response_col_data[key_col] = column_data
                # cur.close()
                # engine.dispose()   
                return Response({"column_data": response_col_data}, status=status.HTTP_200_OK)   
            return Response({'message':"Serializer Error"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])
        


class Measure_Function(CreateAPIView):
    serializer_class = serializers.MeasureInputSerializer
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                database_id = serializer.validated_data['database_id']
                query_set_id =serializer.validated_data['query_set_id']
                table = serializer.validated_data['tables']
                column = serializer.validated_data['columns']
                aggregate = serializer.validated_data['action']  
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            user_id = tok1['user_id']
            if not QuerySets.objects.filter(queryset_id= query_set_id,server_id=database_id,user_id = tok1['user_id']).exists():
                return Response({"message":"Invalid QuerySet Id on Database ID for User"},status=status.HTTP_404_NOT_FOUND)
            try:
                server_details = ServerDetails.objects.get(user_id=user_id, id=database_id)
            except ServerDetails.DoesNotExist:
                return Response({"message": "Server details with the given user ID and database ID do not exist."}, status=status.HTTP_404_NOT_FOUND)

            try:
                ServerType1 = ServerType.objects.get(id=server_details.server_type)
            except ServerType.DoesNotExist:
                return Response({"message": "Server type with the given ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
            # server_conn=columns_extract.server_connection(server_details.username,server_details.password,server_details.database,server_details.hostname,server_details.port,server_details.service_name,ServerType1.server_type.upper(),server_details.database_path)
            # if server_conn['status']==200:
            #     engine=server_conn['engine']
            #     cursor=server_conn['cursor']
            # else:
            #     return Response(server_conn,status=server_conn['status'])
            try:
                clickhouse_class = clickhouse.Clickhouse(server_details.display_name)
                engine=clickhouse_class.engine
                cursor=clickhouse_class.cursor
            except:
                return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                query_data = QuerySets.objects.get(queryset_id = query_set_id)
                data_sourse_string = query_data.custom_query + ' order by 1'
                query = text(data_sourse_string)
                colu = cursor.execute(query)
                col_list = [column for column in colu.keys()]
                alias_data = table_name_from_query(query_data)
                table_aliass = alias_data['table_alias']
                alias_table = alias_data['tables']
                final_alias = associate_tables_with_aliases(table_aliass, alias_table)
                alias = []
                alias.append(final_alias.get(table))
                if column in col_list:
                    if '*' in data_sourse_string:
                        q = data_sourse_string.replace('*', "{}.{}".format(table, column))
                    else:
                        if table_aliass == []:
                            q = re.sub(r'(select\s+)(.*?)(\s+from\s+)', r'\1{}.{}\3'.format(table, column), data_sourse_string, flags=re.IGNORECASE)
                        else:
                            q = re.sub(r'(select\s+)(.*?)(\s+from\s+)', r'\1{}.{}\3'.format(alias[0], column), data_sourse_string, flags=re.IGNORECASE)        
                    query = text(q)                    
                    colu = cursor.execute(query)
                    table_data = colu.fetchall()
                    col_data =[]   
                    for i in table_data:
                        d1 = list(i)
                        col_data.append(d1[0])
                    column_data = np.array(col_data)
                    if np.issubdtype(column_data.dtype, np.number):
                        operation_data = {
                            'sum': np.sum(column_data),
                            'avg': np.mean(column_data),
                            'median': np.median(column_data),
                            'count': len(column_data),
                            'count_distinct': len(set(column_data)),
                            'minimum': np.min(column_data),
                            'maximum': np.max(column_data)
                        }
                    else:
                        operation_data = {
                            'minimum': min(column_data),
                            'maximum': max(column_data),
                            'count': len(column_data),
                            'count_distinct': len(set(column_data))
                        }
                    if aggregate in operation_data:
                        n = f"{aggregate}{column}"
                        response_data = {
                            "queryset_id": query_set_id,
                            "measure":aggregate,
                            "measure_string": f"{aggregate}({column})",
                            f"{aggregate}": operation_data[aggregate]
                            }
                    else:
                        return Response({"message":"no data match"})
                    cursor.close()
                    # engine.dispose()   
                    return Response({"col_data":column,"data":response_data})
                
                else:
                    return Response({'message':"Column doesn't exists"},status=status.HTTP_404_NOT_FOUND)
            
            except Exception as e:
                return Response(f'{e}', status=status.HTTP_404_NOT_FOUND)
            except QuerySets.DoesNotExist:
                return Response({'message': 'Query set not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'Invalid Access Token'},status=status.HTTP_401_UNAUTHORIZED)

class Datasource_column_preview(CreateAPIView):
    serializer_class = serializers.Datasource_preview_serializer
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                database_id = serializer.validated_data['database_id']
                query_set_id =serializer.validated_data['query_set_id']
                table = serializer.validated_data['tables']
                column = serializer.validated_data['columns']
                # data_type = serializer.validated_data['data_type']
                # format1 = serializer.validated_data['format1']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            user_id = tok1['user_id']
            if not QuerySets.objects.filter(queryset_id= query_set_id,server_id=database_id,user_id = tok1['user_id']).exists():
                return Response({"message":"Invalid QuerySet Id on Database ID for User"},status=status.HTTP_404_NOT_FOUND)
            try:
                server_details = ServerDetails.objects.get(user_id=user_id, id=database_id)
            except ServerDetails.DoesNotExist:
                return Response({"message": "Server details with the given user ID and database ID do not exist."}, status=status.HTTP_404_NOT_FOUND)

            try:
                ServerType1 = ServerType.objects.get(id=server_details.server_type)
            except ServerType.DoesNotExist:
                return Response({"message": "Server type with the given ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
            # server_conn=columns_extract.server_connection(server_details.username,server_details.password,server_details.database,server_details.hostname,server_details.port,server_details.service_name,ServerType1.server_type.upper(),server_details.database_path)
            # if server_conn['status']==200:
            #     engine=server_conn['engine']
            #     cur=server_conn['cursor']
            # else:
            #     return Response(server_conn,status=server_conn['status'])
            try:
                clickhouse_class = clickhouse.Clickhouse(server_details.display_name)
                engine=clickhouse_class.engine
                cur=clickhouse_class.cursor
            except:
                return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                query_data = QuerySets.objects.get(queryset_id = query_set_id)
                data_sourse_string = query_data.custom_query + ' order by 1'
                query = text(data_sourse_string)
                colu = cur.execute(query)
                col_list = [column for column in colu.keys()]
                alias_data = table_name_from_query(query_data)
                table_aliass = alias_data['table_alias']
                alias_table = alias_data['tables']
                final_alias = associate_tables_with_aliases(table_aliass, alias_table)
                alias = []
                where_condition = re.search(r'where\s+([^;]+)', data_sourse_string, re.IGNORECASE)
                alias.append(final_alias.get(table))
                
                if column in col_list:
                    if '*' in data_sourse_string:
                        q = data_sourse_string.replace('*', "{}.{}".format(table, column))
                    else:
                        if table_aliass == []:
                            q = re.sub(r'(select\s+)(.*?)(\s+from\s+)', r'\1{}.{}\3'.format(table, column), data_sourse_string, flags=re.IGNORECASE)
                        else:
                            q = re.sub(r'(select\s+)(.*?)(\s+from\s+)', r'\1{}.{}\3'.format(alias[0], column), data_sourse_string, flags=re.IGNORECASE) 
                    query = text(q)                    
                    colu = cur.execute(query)
                    table_data = colu.fetchall()
                    col_data =[]   
                    for i in table_data:
                        d1 = list(i)
                        col_data.append(d1[0])
                    cur.close()
                    # engine.dispose()    
                    return Response({"col_data":column,'row_data':col_data})
                else:
                    return Response({'message':"Column doesn't exists"},status=status.HTTP_404_NOT_FOUND)   
            except Exception as e:
                return Response(f'{e}', status=status.HTTP_404_NOT_FOUND)
            except QuerySets.DoesNotExist:
                return Response({'message': 'Query set not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'Invalid Access Token'},status=status.HTTP_401_UNAUTHORIZED)
        
            
def get_table_alias(tables, table_alias, table_name):
    if table_name in tables:
        index = tables.index(table_name)
        return table_alias[index]
    else:
        return table_alias[tables.index('')]
            

class Datasource_filter(CreateAPIView):
    serializer_class = serializers.Datasource_filter_Serializer
    @transaction.atomic()
    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_datasource_filters])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                database_id = serializer.validated_data['database_id']
                query_set_id =serializer.validated_data['query_set_id']
                tables = serializer.validated_data['tables']
                alias = serializer.validated_data['alias']
                columns = serializer.validated_data['columns']
                data_type  = serializer.validated_data['data_type']
                input_list = serializer.validated_data['input_list']
                format1 = serializer.validated_data['format']
            else:
                return Response({'message':'serializer error'},status=status.HTTP_204_NO_CONTENT)
            
            user_id = tok1['user_id']
            if not QuerySets.objects.filter(queryset_id= query_set_id,server_id=database_id,user_id = tok1['user_id']).exists():
                return Response({"message":"Invalid QuerySet Id on Database ID for User"},status=status.HTTP_404_NOT_FOUND)
                        
            server_details = ServerDetails.objects.get(user_id = user_id,id=database_id)
            ServerType1 = ServerType.objects.get(id = server_details.server_type)
            # server_conn=columns_extract.server_connection(server_details.username,server_details.password,server_details.database,server_details.hostname,server_details.port,server_details.service_name,ServerType1.server_type.upper(),server_details.database_path)
            # if server_conn['status']==200:
            #     engine=server_conn['engine']
            #     cur=server_conn['cursor']
            # else:
            #     return Response(server_conn,status=server_conn['status'])
            try:
                clickhouse_class = clickhouse.Clickhouse(server_details.display_name)
                engine=clickhouse_class.engine
                cur=clickhouse_class.cursor
            except:
                return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
            column_data = []
            try:
                query_data = QuerySets.objects.get(queryset_id = query_set_id)
                # replace_string  = re.search(r'select(.+?)from',  query_data.custom_query, re.DOTALL|re.IGNORECASE)
                data_sourse_string = query_data.custom_query
                format_data = transform_list(input_list)
                alias_data = table_name_from_query(query_data)
                if query_data.is_custom_sql == True:
                    alias_names = alias_data['table_alias']
                    alias_table = alias_data['tables']
                    final_alias = associate_tables_with_aliases(alias_names, alias_table)
                    if alias == [] and alias_names != []:
                        for table in tables:
                            if table in final_alias:
                                alias.append(final_alias[table])
                            else:
                                pass
                    else:
                        pass
                qr=''
                where_condition = re.search(r'where\s+([^;]+)', data_sourse_string, re.IGNORECASE)
                for i in range(len(tables)):
                    if i ==0:
                        fom = str(format_data[i])
                        data = fom.strip("'")
                        if any(dt in data_type[i].lower() for dt in ['char', 'int', 'text']) and not format1[i] in ['end','start','exact','contains','date','time'] or format1[i] in ['selected']:
                            try:
                                if where_condition:
                                    qr += data_sourse_string + f' and {alias[i]}.{columns[i]} in ({format_data[i]})'
                                else:
                                    qr += data_sourse_string + f' where {alias[i]}.{columns[i]} in ({format_data[i]})'
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f' and {tables[i]}.{columns[i]} in ({format_data[i]})'
                                else:
                                    qr += data_sourse_string + f' where {tables[i]}.{columns[i]} in ({format_data[i]})'                        
                        elif 'start' in format1[i].lower():
                            try:
                                if where_condition:
                                    qr += data_sourse_string + f" and  {alias[i]}.{columns[i]} like '{data}%'"
                                else:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '{data}%'"
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f" and  {alias[i]}.{columns[i]} like '{data}%'"
                                else:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '{data}%'"  
                        elif 'end' in format1[i].lower():
                            try:
                                if where_condition:                   
                                    qr += data_sourse_string + f" and  {alias[i]}.{columns[i]} like '%{data}'"
                                else:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '%{data}'"
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f" and  {tables[i]}.{columns[i]} like '%{data}'"
                                else:
                                    qr += data_sourse_string + f" where  {tables[i]}.{columns[i]} like '%{data}'"
                        elif 'contains' in format1[i].lower():
                            try:
                                if where_condition:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '%{data}%'"
                                else:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '%{data}%'"
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f" where  {tables[i]}.{columns[i]} like '%{data}%'"
                                else:
                                    qr += data_sourse_string + f" where  {tables[i]}.{columns[i]} like '%{data}%'"      
                        elif 'exact' in format1[i].lower():         
                            try:
                                if where_condition:
                                    qr += data_sourse_string + f" and  {alias[i]}.{columns[i]} like '{data}'"
                                else:
                                    qr += data_sourse_string + f" where  {alias[i]}.{columns[i]} like '{data}'"
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f" and  {tables[i]}.{columns[i]} like '{data}'"
                                else:
                                    qr += data_sourse_string + f" where  {tables[i]}.{columns[i]} like '{data}'"
                        elif 'date' or 'time' in format1[i].lower():
                            try:
                                if where_condition:
                                    qr += data_sourse_string + f" and TO_CHAR({tables[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]}"
                                else:
                                    qr += data_sourse_string + f" where TO_CHAR({tables[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                            except:
                                if where_condition:
                                    qr += data_sourse_string + f" and TO_CHAR({alias[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                                else:
                                    qr += data_sourse_string + f" where TO_CHAR({alias[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                    else:
                        where_condition2 = re.search(r'where\s+([^;]+)', qr, re.IGNORECASE)
                        fom = str(format_data[i])
                        data = fom.strip("'")                      
                        if any(dt in data_type[i].lower() for dt in ['char', 'int', 'text']) and not format1[i] in ['end','start','exact','contains','date','time'] or format1[i] in ['selected']:
                            try:
                                if where_condition2:
                                    qr += f' and {alias[i]}.{columns[i]} in ({format_data[i]})'
                                else:
                                    qr += f' where {alias[i]}.{columns[i]} in ({format_data[i]})'
                            except:
                                if where_condition2:
                                    qr += f' and {tables[i]}.{columns[i]} in ({format_data[i]})'
                                else:
                                    qr += f' where {tables[i]}.{columns[i]} in ({format_data[i]})'
                        elif 'start' in format1[i].lower():
                            try:
                                if where_condition2:
                                    qr += f" and  {alias[i]}.{columns[i]} like '{data}%'" 
                                else:
                                    qr += f" where  {alias[i]}.{columns[i]} like '{data}%'" 
                            except:  
                                if where_condition2:
                                    qr += f" and  {tables[i]}.{columns[i]} like '{data}%'" 
                                else:
                                    qr += f" where  {tables[i]}.{columns[i]} like '{data}%'" 
                        elif 'end' in format1[i].lower():
                            try:
                                if where_condition2:
                                    qr += f" and {alias[i]}.{columns[i]} like '%{data}'"
                                else:
                                    qr += f" where {alias[i]}.{columns[i]} like '%{data}'"
                            except:
                                if where_condition2:
                                    qr += f" and {alias[i]}.{columns[i]} like '%{data}'"
                                else:
                                    qr += f" where {alias[i]}.{columns[i]} like '%{data}'"
                        elif 'contains' in format1[i].lower():
                            try:
                                if where_condition2:
                                    qr += f" and  {alias[i]}.{columns[i]} like '%{data}%'"
                                else:
                                    qr += f" where  {alias[i]}.{columns[i]} like '%{data}%'" 
                            except:
                                if where_condition2:
                                    qr += f" and  {tables[i]}.{columns[i]} like '%{data}%'"
                                else:
                                    qr += f" where  {tables[i]}.{columns[i]} like '%{data}%'" 
                        elif 'exact' in format1[i].lower():
                            try:
                                if where_condition2:
                                    qr += f" and  {alias[i]}.{columns[i]} like '{data}'" 
                                else:
                                    qr += f" where  {alias[i]}.{columns[i]} like '{data}'" 
                            except:
                                if where_condition2:
                                    qr += f" and  {alias[i]}.{columns[i]} like '{data}'" 
                                else:
                                    qr += f" where  {alias[i]}.{columns[i]} like '{data}'" 
                        elif 'date' or 'time' in format1[i].lower():
                            try:
                                if where_condition2:
                                    qr += f" and TO_CHAR({tables[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]}"
                                else:
                                    qr += f" where TO_CHAR({tables[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                            except:
                                if where_condition2:
                                    qr += f" and TO_CHAR({alias[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                                else:
                                    qr += f" where TO_CHAR({alias[i]}.{columns[i]}, '{format1[i]}') = {format_data[i]} "
                        else:
                            return Response({'message':"Please Select Suitable Format"},status=status.HTTP_400_BAD_REQUEST)                
                if qr.count('where') > 1:
                    qr = remove_second_where_condition(qr)
                else:
                    pass
                data = cur.execute(text(qr))
                col_list = [column for column in data.keys()]
                col_data = data.fetchall()  
                for row in col_data:
                    aa = list(row)
                    column_data.append(aa)
            except Exception as e:
                return Response(f'{e}', status=status.HTTP_404_NOT_FOUND)
            except QuerySets.DoesNotExist:
                return Response({'message': 'Query set not found'}, status=status.HTTP_404_NOT_FOUND)        
            cur.close()
            # engine.dispose()
            models.QuerySets.objects.filter(user_id=tok1['user_id'],queryset_id=query_set_id).update(custom_query = qr,updated_at=updated_at)
            dsf = models.DataSourceFilter.objects.create(
                server_id = database_id,
                user_id = tok1['user_id'],
                queryset_id = query_set_id,
                tables = tables,
                alias = alias,
                datatype = data_type,
                columns = columns,
                custom_selected_data = input_list,
                filter_type = format1
            )
            data ={
                "database_id":database_id,
                "user_id":tok1['user_id'],
                "queryset_id":query_set_id,
                'column_data':col_list,
                'row_data':column_data,
                "is_custom":query_data.is_custom_sql,
                "datasource_filter_id":dsf.filter_id,
                "updated_at":query_data.updated_at
            }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(tok1,status=tok1['status'])



def associate_tables_with_aliases(table_aliass, alias_table):
    table_associations = {}
    for alias, table in zip(table_aliass, alias_table):
        table_associations[table] = alias
    return table_associations


def remove_second_where_condition(query):

    first_where_index = query.lower().find('where')

    if first_where_index != -1:
        second_where_index = query.lower().find('where', first_where_index + 1)
        if second_where_index != -1:
            second_where_end = query.find('\n', second_where_index)
            if second_where_end == -1:
                second_where_end = len(query)
            query = query[:second_where_index] + query[second_where_end:]

    return query.strip()  


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
