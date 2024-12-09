
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
import psycopg2,cx_Oracle,re,pyodbc
from dashboard import models,serializers,views,roles,previlages,files
import pandas as pd
from sqlalchemy import text,inspect
import numpy as np
from quickbooks import models as qb_models
import datetime
import os
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Float, Date, Time, DateTime, Numeric,TIMESTAMP,VARCHAR,BIGINT,SMALLINT,CHAR,Text,TEXT,VARBINARY
from pymongo import MongoClient
from urllib.parse import quote
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def parent_child_ids(id,parameter):
    try:
        prid=models.parent_ids.objects.get(id=id,parameter=parameter)
    except:
        data = {'Id not exists'}
        return data
    if parameter=="quickbooks":
        ch_id=qb_models.TokenStoring.objects.get(id=prid.table_id)
        child_id=ch_id.qbuserid
    elif parameter=="salesforce":
        ch_id=qb_models.TokenStoring.objects.get(id=prid.table_id)
        child_id=ch_id.salesuserid
    elif parameter=="server":
        ch_id=models.ServerDetails.objects.get(id=prid.table_id)
        child_id=ch_id.id
    elif parameter=="files":
        ch_id=models.FileDetails.objects.get(id=prid.table_id)
        child_id=ch_id.id
    return child_id


def server_connection(username, password, database, hostname,port,service_name,parameter,server_path):
    try:
        password1234=views.decode_string(password)
    except:
        pass
    # engine = None
    # cursor = None
    try:
        if parameter=="POSTGRESQL":
            url = "postgresql://{}:{}@{}:{}/{}".format(username,password1234,hostname,port,database)
        elif parameter=="ORACLE":
            url = 'oracle+cx_oracle://{}:{}@{}:{}/{}'.format(username,password1234,hostname,port,service_name)
        elif parameter=="MYSQL":
            url = f'mysql+mysqlconnector://{username}:{password1234}@{hostname}:{port}/{database}'
        elif parameter=="SNOWFLAKE":
            encoded_password = quote(password1234)
            url = f'snowflake://{username}:{encoded_password}@{hostname}/{database}?port={port}'
        elif parameter=="IBMDB2":
            url = f'ibm_db_sa://{username}:{password1234}@{hostname}:{port}/{database}'
        elif parameter=="MICROSOFTSQLSERVER":
            driver='ODBC Driver 17 for SQL Server'
            # connection_string = f'DRIVER={driver};SERVER={hostname};DATABASE={database};Trusted_Connection=yes;' 
            connection_string = f'DRIVER={{{driver}}};SERVER={hostname};DATABASE={database};UID={username};PWD={password1234};Trusted_Connection=yes;' #
            conn = pyodbc.connect(connection_string)
        elif parameter=="MICROSOFTACCESS" or parameter=="SQLITE":
            sq_msacces=server_path_function(server_path,parameter)
            if sq_msacces['status']==200:
                url = sq_msacces['url']
            else:
                return sq_msacces
        elif parameter=="SYBASE":
            url = f'sybase+pyodbc://{username}:{password1234}@{hostname}:{port}/{database}'
        elif parameter=="MONGODB":
            mongo=mongo_db(username, password, database, hostname,port)
            return mongo
        elif parameter=="CASSANDRA":
            auth_provider = PlainTextAuthProvider(username=username, password=password1234)
            cluster = Cluster([hostname], port=port, auth_provider=auth_provider)
            cassandra = cassandra_db(cluster)
            return cassandra
        elif parameter=="SAP HANA":
            connection_string = f"hana+hdbcli://{username}:{password1234}@{hostname}:{port}/{database}"
        elif parameter=="SAP BW":
            connection_string = f"hana+hdbcli://{username}:{password1234}@{hostname}:{port}/{database}"
            
        # engine = create_engine(url, echo=True)
        if parameter=="MICROSOFTSQLSERVER": 
            if int(port)==1433:
                engine = conn
                cursor = conn.cursor()
            else:
                data={
                    "status":400,
                    "message":"Invalid port"
                }
                return data
        else:
            engine = create_engine(url)
            cursor = engine.connect()

        data={
            "status":200,
            "engine":engine,
            "cursor":cursor
        }
        return data
    except Exception as e:
        data={
            "status":400,
            # "message" : f"{str(e)}"
            "message":"Invalid credientials or database server issue"
        }
        return data
    # finally:
    #     # Close the connection if it was established
    #     if cursor:
    #         cursor.close()
    #     if engine:
    #         engine.dispose() 


def cassandra_db(cluster):
    try:
        session = cluster.connect()
        # print("Connected to cluster:", cluster.metadata.cluster_name)
        cluster.shutdown()
        data = {
            "status":200,
            "engine":None,
            "cursor":None
        }
        return data
    except Exception as e:
        data={
            "status":400,
            "message" : f"{str(e)}"
        }
        return data

def mongo_db(username, password, database, hostname, port):
    try:
        if username=='' or None and password =='' or None:
            client = MongoClient(hostname, int(port))
        else:
            connection_string = f'mongodb://{username}:{password}@{hostname}:{int(port)}/{database}'
            client = MongoClient(connection_string)
        
        db = client[database]
        data = {
            "status":200,
            "engine":db,
            "cursor":None
        }
        return data
    except Exception as e:
        data={
            "status":400,
            "message" : f"{str(e)}"
        }
        return data
    

def server_path_function(server_path,parameter):
    if server_path==None or server_path=='':
        data = {
            "status":406,
            "message":"database_path is mandatory"
        }
        return data
    else:
        if parameter=="MICROSOFTACCESS":
            # database_path = r'C:\path\to\your\database.accdb'
            url = f'access+pyodbc:///?Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={str(server_path)}'
        elif parameter=="SQLITE":
            # database_path = 'path/to/your/database.db'
            # url = f'sqlite:///{str(server_path)}'
            file_name, file_extension = files.fetch_filename_extension(server_path)
            if file_extension =='.db' or file_extension=='.sqlite' or file_extension=='.sqlite3' or file_extension=='':
                pass
            else:
                data = {
                    "status":406,
                    "message":"not acceptable/invalid file"
                }
                return data
            try:
                BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
                db_file_path = os.path.join(BASE_DIR, str(server_path))
                url = f'sqlite:///{db_file_path}'
            except:
                # database_path = 'path/to/your/database.db'
                url = f'sqlite:///{str(server_path)}'
        data = {
            "status":200,
            "url":url
        }
        return data


    
def get_sqlalchemy_type(type_code):
    type_code_map = {
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
    # Add other type codes as needed
}
    value =type_code_map.get(type_code, String)()
    return value


def file_check(para,file_name):
    project_directory = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = Path(__file__).resolve().parent.parent
    db_file_path = os.path.join(BASE_DIR, str(file_name))

    if para=='check':
        if not os.path.exists(db_file_path):
            open(db_file_path, 'a').close()
        else:
            pass
    else:
        os.remove(db_file_path)
        open(db_file_path, 'a').close()
        

def excel_file_data(xls,sheet_name):
    BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
    db_file_path = os.path.join(BASE_DIR, 'columns.db')
    url = f'sqlite:///{db_file_path}'  # Use the dynamic path for the SQLite database
    
    for i in xls.sheet_names:
        sheet_name.append(i)
        data_csv = pd.read_excel(xls,sheet_name=i)
        data_csv = data_csv.fillna(value='NA')
        # url =f'sqlite:///columns.db'
        engine = create_engine(url)
        for column in data_csv.columns:
            if data_csv[column].dtype == 'object':
                data_csv[column] = data_csv[column].astype(str)  # Convert to TEXT
            elif data_csv[column].dtype == 'int64':
                data_csv[column] = data_csv[column].astype(int)  # Convert to INTEGER
            elif data_csv[column].dtype == 'float64':
                data_csv[column] = data_csv[column].astype(float)
        data_csv.to_sql(i, engine, index=False, if_exists='replace')
    data = {
        'engine':engine,
        'sheet_name':sheet_name
    }
    return data

def read_excel_file_data(file_path,filename):
    try:
        encoded_url = quote(file_path, safe=':/')
        xls = pd.ExcelFile(encoded_url)
        l=[]
        sheet_name = []
        file_check('check',file_name='columns.db')
        try:
            excl_dt=excel_file_data(xls,sheet_name)
        except:
            file_check('remove',file_name='columns.db')
            excl_dt=excel_file_data(xls,sheet_name)

        f_dt = {
            "status":200,
            "engine":excl_dt['engine'],
            "cursor":excl_dt['engine'].connect(),
            "tables_names":excl_dt['sheet_name']
        }
        return f_dt
    except Exception as e:
        f_dt = {
            "status":400,
            "message":"Un-Supported file format/file is not readable"
        }
        return f_dt


def read_csv_file_data(file_path,filename):
    try:
        df = pd.read_csv(file_path)
        df = df.fillna(value='NA')
        file_check('check',file_name='columns.db')
        BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
        db_file_path = os.path.join(BASE_DIR, 'columns.db')
        url = f'sqlite:///{db_file_path}'
        # url =f'sqlite:///columns.db'
        try:
            engine = create_engine(url)
            df.to_sql(filename, engine, index=False, if_exists='replace')
        except:
            file_check('remove',file_name='columns.db')
            engine = create_engine(url)
            df.to_sql(filename, engine, index=False, if_exists='replace')
            
        f_dt = {
                "status":200,
                "engine":engine,
                "cursor":engine.connect(),
                "tables_names":filename
            }
        return f_dt
    except Exception as e:
        f_dt = {
            "status":400,
            "message":"Un-Supported file format/file is not readable"
        }
        return f_dt
    

def columns_first_data(codes,result):
    seen_columns = {}
    column_list = []
   
    for column in codes:
        try:
            column_name = column[0]
        except:
            column_name = column
        if column_name in seen_columns:
            seen_columns[column_name] += 1
            column_name = f"{column_name}_{seen_columns[column_name]}"
        else:
            seen_columns[column_name] = 0
        column_list.append(column_name)

    # filtered_records = []
    all_records=result.fetchall()
    # filtered_records = [record for record in all_records if all(field != '' for field in record)]
    def is_valid_tuple(t):
        return all(x not in (None, '', "") for x in t)
    filtered_records = [t for t in all_records if is_valid_tuple(t)]
    try:
        if filtered_records:
            return filtered_records[0]
        else:
            return all_records[-1]
    except:
        return []

    #### fetch first record
    # first_record = result.fetchone()
    # print(first_record)
    #### fetch last record
    # all_records = result.fetchall()
    # first_record = all_records[-1]
    # print(first_record)
    # column_wise_first_record = {}
    # if first_record is not None:
    #     for index, column_name in enumerate(column_list):
    #         column_wise_first_record[column_name] = first_record[index]
    # data_values = list(column_wise_first_record.values())
    # return data_values

        
    

def classify_data_type(value):
    int_pattern = r'^\d+$'
    bool_pattern = r'^(True|False|true|false)$'
    float_pattern = r'^-?\d+(\.\d+)?$'
    if isinstance(value, bool):  # Rule for Boolean
        return 'bool'
    elif isinstance(value, int):  # Rule for Integer
        return 'integer'
    elif isinstance(value, float):  # Rule for Float
        return 'float'
    elif isinstance(value, datetime.datetime):  # Rule for Datetime
        return 'datetime'
    elif isinstance(value, datetime.date):  # Rule for Date
        return 'date'
    elif isinstance(value, str):  # Rule for String-based types
        date_patterns = [
            r'^(?:\d{1,2}|[a-zA-Z]{3})-\d{1,2}-\d{4}$',  # dd-mm-yyyy or mon-mm-yyyy
            r'^(?:\d{1,2}|[a-zA-Z]{3})/\d{1,2}/\d{4}$',  # dd/mm/yyyy or mon/mm/yyyy
        ]
        datetime_patterms = [
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$',  # yyyy-mm-dd HH:MM:SS.ssssss
            r'^\d{4}-[a-zA-Z]{3}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$',  # yyyy-mon-dd HH:MM:SS.ssssss
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$',  # yyyy/mm/dd HH:MM:SS.ssssss
            r'^\d{4}/[a-zA-Z]{3}/\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$',   # yyyy/mon/dd HH:MM:SS.ssssss
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}$',
            r'^\d{4}-[a-zA-Z]{3}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}$',
            r'^\d{4}/[a-zA-Z]{3}/\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}$',
        ]
        # Check the value against each date and datetime pattern
        for date_p in date_patterns:
            if re.match(date_p, value):
                return 'date'
        for datetime_p in datetime_patterms:
            if re.match(datetime_p, value):
                return 'datetime'
        # Clean the value for further checks
        value = value.replace(' ', '').replace('_', '')
        if re.match(r'^[a-zA-Z]+$', value):  # Rule for pure string
            return 'string'
        elif re.match(int_pattern, value):  # Rule for Integer-like string
            return 'integer'
        elif re.match(r'^[a-zA-Z0-9]+$', value):  # Rule for alphanumeric (varchar)
            return 'varchar'
        else:
            return 'varchar'
    # Default case: If none of the above, consider it as varchar
    else:
        return 'varchar'


def delete_tables_sqlite(cur,engine,tables):
    # if len(tables)>0:
    #     for table1 in tables:
    #         drop_table_sql = f'DROP TABLE IF EXISTS \"{table1}\";'
    #         a= cur.execute(text(drop_table_sql))
    #         cur.commit()
    #         print(a)
    #         # engine.commit()
    try:
        with cur as connection:
            if len(tables) > 0:
                for table in tables:
                    drop_table_sql = text(f'DROP TABLE IF EXISTS \"{table}\";')
                    connection.execute(drop_table_sql)
            connection.commit()
    except Exception as e:
        print(e)

    
def file_details(file_type,file_data):
    try:
        if file_type is not None or  file_data !='' or file_data is not  None or file_data !='':
            file_url=file_data.source
            file, fileext = os.path.splitext(os.path.basename(file_data.display_name))
            # file = file.split('_IN:')[-1]
            if (file_type.upper()=='EXCEL' and fileext == '.xlsx') or (file_type.upper()=='EXCEL' and fileext == '.xls'):
                read_data = read_excel_file_data(file_url,file)
            elif  file_type.upper()=='CSV' and fileext == '.csv':
                read_data = read_csv_file_data(file_url,file)
            else:
                data = {
                    'status':400,
                    'message':'No Data/ Invalid file type'
                }
                return data

            if read_data['status'] ==200:
                data = {
                    'status':200,
                    'engine':read_data['engine'],
                    'cursor':read_data['cursor'],
                    'tables_names':read_data['tables_names']
                } 
            else:
                data = {
                    'status':int(read_data['status']),
                    'message':read_data
                }
            return data
        else:
            data = {
                'status':400,
                'message':'no Data/database locked'
            }
            return data 
    except:
        data = {
            'status':400,
            'message':'no Data/database locked'
        }
        return data
    


def classify_columns(column_wise_first_record,names, type,table_alias):
    types=[str(col).replace("()", '').lower() for col in type]
    dimension_types = ['String','string','Date', 'TIMESTAMP', 'Boolean','bool', 'Time', 'datetime','varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying','date','time','datetime','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone','bool','boolean']
    measure_types = ['Integer', 'Float', 'Numeric', 'int', 'float','numeric','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double']
    dimensions = []
    measures = []

    if column_wise_first_record==None or column_wise_first_record==[]:
        classified_data_types_fn=types
    else:
        classified_data_types = [classify_data_type(value) for value in column_wise_first_record]
        if classified_data_types==[] or classified_data_types==None:
            classified_data_types_fn=types
        else:
            classified_data_types_fn=classified_data_types

    # Update the data types based on column names
    # for name1,i,tp1,cl_dt in zip(names,range(len(names)),classified_data_types_fn,column_wise_first_record): #types,column_wise_first_record
    #     try:
    #         column_name = names[i].lower()
    #         current_data_type = classified_data_types_fn[i].lower()
    #     except:
    #         column_name = str(name1).lower()
    #         current_data_type = str(tp1).lower()
        # if any(keyword in column_name for keyword in ['_id', '_Id', '_ID', 'ID', 'id', 'Id']) and current_data_type == 'varchar' and 'email' not in column_name.lower():
        #     classified_data_types_fn[i] = 'int'
        # elif any(keyword in column_name for keyword in ['date', 'time', 'login','Date']):  #, 'start', 'end'
        #     classified_data_types_fn[i] = 'date'
        # elif any(keyword in column_name for keyword in ['is_', 'Is_']) and current_data_type == 'varchar':  #, 'start', 'end'
        #     classified_data_types_fn[i] = 'bool'
    # for name, dtype,cl_data in zip(names,types,column_wise_first_record):
    for i,name1,tp1 in zip(range(len(names)),names,classified_data_types_fn):
        try:
            column_name = names[i].lower()
            current_data_type = classified_data_types_fn[i].lower()
        except:
            column_name = str(name1).lower()
            current_data_type = str(tp1).lower()
        if any(keyword in column_name for keyword in ['login','date','time']) and current_data_type == str(String) :  #, 'start', 'end'
            classified_data_types_fn[i] = 'datetime'
        elif any(keyword in column_name for keyword in ['address','adress','city']) and (current_data_type == str(int) or current_data_type == str(Date) or current_data_type == str(DateTime)):  #, 'start', 'end'
            classified_data_types_fn[i] = 'varchar'
        elif any(keyword in column_name for keyword in ['postal']):  #, 'start', 'end'
            classified_data_types_fn[i] = 'integer'
        elif any(keyword in column_name for keyword in ['_id', '_Id', '_ID', 'ID', 'id', 'Id']) and current_data_type == str(String) and 'email' not in column_name.lower():
            classified_data_types_fn[i] = 'integer'
        elif any(keyword in column_name for keyword in ['is_', 'Is_']) and current_data_type == str(String):  #, 'start', 'end'
            classified_data_types_fn[i] = 'bool'
    for name, dtype in zip(names,classified_data_types_fn):
        # if table_alias in name:
        #     output_string = name.replace(f"({table_alias})", "").strip()
        #     output_string = output_string.replace("()", "").strip()
        # else:
        #     output_string=name
        if dtype in dimension_types:
            dimensions.append({"column":name,"data_type":str(dtype),"table_name":table_alias,}) #"actual_column":output_string
        elif dtype in measure_types:
            measures.append({"column":name,"data_type":str(dtype),"table_name":table_alias}) #"actual_column":output_string
        else:
            dimensions.append({"column":name,"data_type":'string',"table_name":table_alias}) #"actual_column":output_string
    return dimensions, measures


def snowflake_data(query):
    table_pattern = re.compile(
        r'FROM\s+([\w\d]+)\.([\w\d]+)\s+AS\s+"([\w\d_]+)"'  # Match FROM clause with schema, table, alias
        r'|JOIN\s+([\w\d]+)\.([\w\d]+)\s+AS\s+"([\w\d_]+)"',  # Match JOIN clause with schema, table, alias
        re.IGNORECASE
    )
    column_pattern = re.compile(
        # r'"(\w+)"\.(\w+)\s+AS\s+"(\w+)"',  # Match column with alias
        r'"([\w\d_]+)"\.(\w+)\s+AS\s+"(\w+)"',  # Match column with alias
        re.IGNORECASE
    )
    table_matches = table_pattern.findall(query)
    tables_info = {}
    for match in table_matches:
        if match[0]:  # FROM clause matched
            schema_name, table_name, table_alias = match[0], match[1], match[2]
        else:  # JOIN clause matched
            schema_name, table_name, table_alias = match[3], match[4], match[5]
        if not table_alias:
            table_alias = table_name
        tables_info[table_alias] = (schema_name, table_name)
    op = re.sub(r'\(.*?\)', '', query)
    column_matches = column_pattern.findall(op)
    columns_info = []
    for match in column_matches:
        table_alias, column_name, column_alias = match[0], match[1], match[2]
        schema_name, table_name = tables_info.get(table_alias, (None, None))
        columns_info.append({
            "schema": schema_name,
            "table_name": table_name,
            "table_alias": table_alias,
            "column_name": column_name,
            "column_alias": column_alias
        })
    return columns_info


def search_columns(search,cleaned_data):
    if search=='' or search==None:
        data_fn=cleaned_data
    else:
        # data_fn=[item for item in cleaned_data if str(search).lower() in item.get('table_alias', '').lower()]
        result = []
        for table in cleaned_data:
            filtered_dimensions = [dim for dim in table["dimensions"] if str(search).lower() in dim["column"].lower()]
            filtered_measures = [meas for meas in table["measures"] if str(search).lower() in meas["column"].lower()]
            if filtered_dimensions or filtered_measures:
                filtered_table = table.copy()
                filtered_table["dimensions"] = filtered_dimensions
                filtered_table["measures"] = filtered_measures
                result.append(filtered_table)
        data_fn=result  
    return data_fn


def query_filter(sql_query,server_type):
    if server_type=="SNOWFLAKE":
        snowflake=snowflake_data(str(sql_query))
        return snowflake
    else:
        table_pattern = re.compile(r'FROM\s+"([^"]+)"\."([^"]+)"\s+("([^"]+)")?|JOIN\s+"([^"]+)"\."([^"]+)"\s+("([^"]+)")?', re.IGNORECASE)
        table_matches = table_pattern.findall(str(sql_query))
        tables_info = {}
        for match in table_matches:
            if match[0]:
                schema_name, table_name, _, table_alias = match[0], match[1], match[2], match[3]
            else:
                schema_name, table_name, _, table_alias = match[4], match[5], match[6], match[7]
            tables_info[table_alias] = (schema_name, table_name)
        column_pattern = re.compile(r'"([^"]+)"\."([^"]+)"\s+as\s+"([^"]+)"', re.IGNORECASE)
        column_matches = column_pattern.findall(str(sql_query))
        columns_info = []
        for table_alias, column_name, column_alias in column_matches:
            schema_name, table_name = tables_info.get(table_alias, ('public', table_alias))
            columns_info.append({
                "schema": schema_name,
                "table_name": table_name,
                "table_alias": table_alias,
                "column_name": column_name,
                "column_alias": column_alias
            })
        return columns_info
    

def custom_sql(search,quer_tb,column_wise_first_record,cursor,type_codes,column_list,ser_db_data,server_details_id,queryset_id,data_types,user_id,parameter):
    if parameter=="file":
        server_id=None
        file_id=server_details_id
    else:
        server_id=server_details_id
        file_id=None
    if data_types==None or data_types=='':
        dt_list=[]
        for i in type_codes:
            a1=get_sqlalchemy_type(i) 
            dt_list.append(a1)
        dt_list=dt_list
    else:
        dt_list=data_types
    table_alias='Custom_query'
    dimensions,measures=classify_columns(column_wise_first_record,column_list,dt_list,table_alias)
    fl_data=[]
    data = {
        "database_name":ser_db_data.display_name,
        "server_id":server_id,
        "file_id":file_id,
        "queryset_id":queryset_id,
        "is_custom_sql":quer_tb.is_custom_sql,
        "schema":"",
        "table_name":"Custom_query",
        "table_alias":table_alias,
        "dimensions":dimensions,
        "measures":measures,
    }
    fl_data.append(data)
    data_fn=search_columns(search,fl_data)
    calf_vale=models.calculation_field.objects.filter(user_id=user_id,queryset_id=queryset_id).values().order_by('-updated_at')
    fn_val=list(calf_vale)
    for fn_cl in fn_val:
        fn_cl['column']=fn_cl['cal_logic']
        del fn_cl['cal_logic']
        # del fn_cl['actual_dragged_logic']
        fn_cl['data_type']='calculated'
        fn_cl['format']='None'
    if fn_val==[] or fn_val==None:
        data_fn=data_fn
    else:
        cal_d1={
            'calculated_fields':fn_val
        }
        data_fn.append(cal_d1)
    return Response(data_fn,status=status.HTTP_200_OK)

def joining_sql(column_wise_first_record,search,cursor,type_codes,engine,quer_tb,queryset_id,server_id,ser_db_data,server_type,data_types,user_id,parameter):
    if parameter=="file":
        server_id1=None
        file_id=server_id
    else:
        server_id1=server_id
        file_id=None
    # ##
    # classified_data_types = [classify_data_type(value) for value in column_wise_first_record]
    # if classified_data_types==[] or classified_data_types==None:
    #     if data_types==None or data_types=='':
    #         dt_list=[]
    #         for i in type_codes:
    #             a1=get_sqlalchemy_type(i) 
    #             dt_list.append(a1)
    #         dt_list=dt_list
    #     else:
    #         dt_list=data_types
    #     classified_data_types_fn=dt_list
    # else:
    #     classified_data_types_fn=classified_data_types
    # ##
    if data_types==None or data_types=='':
        dt_list=[]
        for i in type_codes:
            a1=get_sqlalchemy_type(i) 
            dt_list.append(a1)
        dt_list=dt_list
        # dt_list=classified_data_types_fn
    else:
        dt_list=data_types
        # dt_list=classified_data_types_fn

    if server_type=="MICROSOFTSQLSERVER":
        clea_qr=str(quer_tb.custom_query).replace('[','"').replace(']','"')
        query1 = "{}".format(clea_qr)
        qr_flter=query_filter(query1,server_type)
    elif server_type=="MYSQL":
        clea_qr=str(quer_tb.custom_query).replace('`','"')
        qr_flter=query_filter(text(clea_qr),server_type)
    else:
        qr_flter=query_filter(text(quer_tb.custom_query),server_type)
    if len(dt_list) < len(qr_flter):
        dt_list += [None] * (len(qr_flter) - len(dt_list))   ## adding null for no datatype
    for clmn, dt_tp in zip(qr_flter, dt_list):
        clmn['data_type'] = dt_tp    ## adding column wise datatypes
    tables_dict = {}
    for item in qr_flter:
        table_alias = item['table_alias']
        table_name = item['table_name']
        if table_alias not in tables_dict:
            tables_dict[table_alias] = {
                'schema': item['schema'],
                'table_name': table_name,
                'table_alias': table_alias,
                'columns': [],
                'dimensions':[],
                'measures':[]
            }
        column_info = {
            'column': item['column_alias'],
            'data_type': item['data_type']
        }
        tables_dict[table_alias]['columns'].append(column_info) # adding table wise columns,datatypes to existing data
    res1=list(tables_dict.items())
    def fetch_columns(table_alias):
        for table_tuple in res1:
            if table_tuple[0] == table_alias:
                return table_tuple[1]['columns']
        return None
    for table_index, (table_alias, table_data) in enumerate(res1):
        user_columns = fetch_columns(str(res1[table_index][1]['table_alias'])) # to fetch table wise columns,datatypes
        cls1=[]
        dts1=[]
        for i in user_columns:
            cls1.append(i['column'])
            dts1.append(i['data_type'])
        # column_wise_first_record1=[]
        dimensions,measures=classify_columns(column_wise_first_record,cls1,dts1,table_alias)
        del res1[table_index][1]['columns']  # Remove the 'columns' key from the table data
        res1[table_index][1]['dimensions'] = dimensions
        res1[table_index][1]['measures'] = measures
        res1[table_index][1]['database_name'] = ser_db_data.display_name
        res1[table_index][1]['server_id'] = server_id1
        res1[table_index][1]['file_id'] = file_id
        res1[table_index][1]['queryset_id'] = queryset_id
        res1[table_index][1]['is_custom_sql'] = quer_tb.is_custom_sql
        cls1.clear()
        dts1.clear()
    flat_filters_data = [item for sublist in res1 for item in sublist] # to remove extra list
    cleaned_data = [item for item in flat_filters_data if isinstance(item, dict)] # to remove the data other than in dict
    if server_type=="SNOWFLAKE":
        cleaned_data=cleaned_data
    else:
        cleaned_data=cleaned_data[:-1]
    data_fn=search_columns(search,cleaned_data)
    calf_vale=models.calculation_field.objects.filter(user_id=user_id,queryset_id=queryset_id).values().order_by('-updated_at')
    fn_val=list(calf_vale)
    for fn_cl in fn_val:
        fn_cl['column']=fn_cl['cal_logic']
        del fn_cl['cal_logic']
        # del fn_cl['actual_dragged_logic']
        fn_cl['data_type']='calculated'
        fn_cl['format']='None'
    if fn_val==[] or fn_val==None:
        data_fn=data_fn
    else:
        cal_d1={
            'calculated_fields':fn_val
        }
        data_fn.append(cal_d1)
    # data_fn[0]['calculated_fields']=fn_val
    return Response(data_fn,status=status.HTTP_200_OK)


def mongo_db_data(engine,display_name,server_id,queryset_id):
    db=engine
    final_list={}
    colms=[]
    final_ls=[]
    collections = db.list_collection_names()
    for collection_name in collections:
        final_list['schema']=None
        final_list['table_name']=collection_name
        final_list['table_alias']=collection_name
        collection = db[collection_name]
        documents = collection.find()
        for field in documents:
            data = {
                'column':field,
                'data_type':None
            }
            # colms.append({'column':field,'data_type':None})
            colms.append(data)
            final_list['dimensions']=colms
            final_list['measures']=[]
            final_list['database_name']=display_name
            final_list['server_id']=server_id
            final_list['queryset_id']=queryset_id
    final_ls.append(final_list)
    return final_ls


#### Columns extraction from table
class new_column_extraction(CreateAPIView):
    serializer_class=serializers.new_table_input

    def post(self,request,token):
        role_list=roles.get_previlage_id(previlage=[previlages.create_sheet,previlages.view_sheet,previlages.edit_sheet])
        tok1 = roles.role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  
                server_details_id=serializer.validated_data['db_id']
                queryset_id=serializer.validated_data['queryset_id']
                file_id=serializer.validated_data['file_id']
                search=serializer.validated_data['search']
                if server_details_id==None or server_details_id=='':
                    try:
                        file_db_data=models.FileDetails.objects.get(id=file_id)
                        file_data=models.FileType.objects.get(id=file_db_data.file_type)
                    except:
                        return Response({'message':'file_details_id/file_type not exists'},status=status.HTTP_404_NOT_FOUND)
                    try:
                        quer_tb=models.QuerySets.objects.get(queryset_id=queryset_id,file_id=file_id)  #,user_id=tok1['user_id']
                    except:
                        return Response({'message':'Queryset id not matching with the user files details'},status=status.HTTP_406_NOT_ACCEPTABLE)
                elif file_id==None or file_id=='':
                    try:
                        ser_db_data=models.ServerDetails.objects.get(id=server_details_id,is_connected=True)
                        ser_data=models.ServerType.objects.get(id=ser_db_data.server_type)
                    except:
                        return Response({'message':'server_details_id/server_type not exists'},status=status.HTTP_404_NOT_FOUND)
                    try:
                        quer_tb=models.QuerySets.objects.get(queryset_id=queryset_id,server_id=server_details_id)  #,user_id=tok1['user_id']
                    except:
                        return Response({'message':'Queryset id not matching with the user server details'},status=status.HTTP_406_NOT_ACCEPTABLE)
    
                column_wise_first_record = {}
                if server_details_id==None or server_details_id=='':
                    files_data = file_details(file_data.file_type,file_db_data)
                    if files_data['status']==200:
                        engine=files_data['engine']
                        cursor=files_data['cursor']
                        result=cursor.execute(text(quer_tb.custom_query))
                        codes=result.cursor.description
                        type_codes = [column[1] for column in codes]
                        column_list = [column[0] for column in codes]
                        data_types=None
                        column_wise_first_record=columns_first_data(codes,result)
                        # column_wise_first_record=None
                    else:
                        return Response({"message":files_data['message']},status=files_data['status'])
                    if quer_tb.is_custom_sql==True:
                        custom=custom_sql(search,quer_tb,column_wise_first_record,cursor,type_codes,column_list,file_db_data,file_id,queryset_id,data_types,tok1['user_id'],parameter="file")
                        delete_tables_sqlite(cursor,engine,files_data['tables_names'])
                        cursor.close()
                        # engine.dispose()
                        return custom
                    else:
                        joining=joining_sql(column_wise_first_record,search,cursor,type_codes,engine,quer_tb,queryset_id,file_id,file_db_data,file_data.file_type.upper(),data_types,tok1['user_id'],parameter="file")
                        delete_tables_sqlite(cursor,engine,files_data['tables_names'])
                        cursor.close()
                        # engine.dispose()
                        return joining
                elif file_id==None or file_id=='':
                    connect1=server_connection(ser_db_data.username,ser_db_data.password,ser_db_data.database,ser_db_data.hostname,ser_db_data.port,ser_db_data.service_name,ser_data.server_type.upper(),ser_db_data.database_path)
                    if connect1['status']==200:
                        engine=connect1['engine']
                        cursor=connect1['cursor']
                        if ser_data.server_type.upper()=="MONGODB":
                            mongo=mongo_db_data(engine,ser_db_data.display_name,server_details_id,queryset_id)
                            return mongo
                        else:
                            if ser_data.server_type.upper()=="MICROSOFTSQLSERVER":
                                query = "{}".format(quer_tb.custom_query)
                                result = cursor.execute(query)
                                codes = cursor.description
                                column_list = [column[0] for column in codes]
                                type_codes = [column[1] for column in codes]
                                data_types = [data_type[1].__name__ for data_type in codes]
                                # column_wise_first_record=columns_first_data(codes,result)
                            else:
                                result=cursor.execute(text(quer_tb.custom_query))
                                codes=result.cursor.description
                                type_codes = [column[1] for column in codes]
                                column_list = [column[0] for column in codes]
                                data_types=None
                                # column_wise_first_record=columns_first_data(codes,result)
                        column_wise_first_record=None
                    else:
                        return Response({"message":connect1['message']},status=connect1['status'])
                    if quer_tb.is_custom_sql==True:
                        custom=custom_sql(search,quer_tb,column_wise_first_record,cursor,type_codes,column_list,ser_db_data,server_details_id,queryset_id,data_types,tok1['user_id'],parameter="server")
                        cursor.close()
                        # engine.dispose()
                        return custom
                    else:
                        joining=joining_sql(column_wise_first_record,search,cursor,type_codes,engine,quer_tb,queryset_id,server_details_id,ser_db_data,ser_data.server_type.upper(),data_types,tok1['user_id'],parameter="server")
                        cursor.close()
                        # engine.dispose()
                        return joining
                else:
                    return Response({'message':'not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])