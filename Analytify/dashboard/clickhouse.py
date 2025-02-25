import pandas as pd
import io,os,clickhouse_connect
from sqlalchemy import create_engine
import concurrent.futures
import pandas as pd
import boto3
from project import settings
from django.core.files.base import ContentFile
from functools import partial
import numpy as np
from concurrent.futures import ThreadPoolExecutor



integer_list=['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double','int64','int32','float64','float32','nullable(int64)', 'nullable(int32)', 'nullable(uint8)', 
    'nullable(float(64))','int8','int16','int32','int64','float32','float16','float64','decimal(38,10)','decimal(12,2)','uuid','nullable(int8)','nullable(int16)','nullable(int32)','nullable(int64)','nullable(float32)','nullable(float16)','nullable(float64)','nullable(decimal(38,10)','nullable(decimal(12,2)']
char_list=['varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying','string','str','nullable(varchar)', 'nullable(bp char)', 'nullable(text)', 
    'nullable(varchar2)', 'nullable(NVchar2)', 
    'nullable(long)', 'nullable(char)', 'nullable(Nchar)', 
    'nullable(character varying)', 'nullable(string)','string','nullable(string)','array(string)','nullable(array(string))']
bool_list=['bool','boolean','nullable(bool)', 'nullable(boolean)','uint8']
date_list=['date','time','datetime','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone','timestamptz','nullable(date)', 'nullable(time)', 'nullable(datetime)', 
    'nullable(timestamp)', 
    'nullable(timestamp with time zone)', 
    'nullable(timestamp without time zone)', 
    'nullable(timezone)', 'nullable(time zone)', 'nullable(timestamptz)', 
    'nullable(datetime)','datetime64','datetime32','date32','nullable(date32)','nullable(datetime64)','nullable(datetime32)','date','datetime','time','datetime64','datetime32','date32','nullable(date)','nullable(time)','nullable(datetime64)','nullable(datetime32)','nullable(date32)'] 


try:
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
except Exception as e:
    print(e)


def file_files_save(file_path, file_path112):
    if settings.file_save_path == 's3':
        t1=str(file_path)
        file_path1 = f'insightapps/{t1}.csv'
        try:
            # If file_path112 is already a file-like object, attempt to upload directly
            s3.upload_fileobj(file_path112, settings.AWS_STORAGE_BUCKET_NAME, file_path1)
        
        except Exception as e:
            try:
                # If file_path112 has a temporary file path (common with uploaded files in Django), read it as binary
                if hasattr(file_path112, 'temporary_file_path'):
                    with open(file_path112.temporary_file_path(), 'rb') as data:
                        s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1)
                else:
                    # If file_path112 doesn’t have a temporary path, assume it is binary content and read directly
                    data = ContentFile(file_path112.read())  # Read binary data as content
                    s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1)

            except Exception as e:
                return None

        # Construct and return the S3 URL of the uploaded file
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_path1}"
        return file_url

from clickhouse_connect.driver.tools import insert_file

import csv



# def map_dtype(dtype):
#     dtype_mapping = {
#         pd.api.types.is_integer_dtype: 'Int64',
#         pd.api.types.is_float_dtype: 'Float64',
#         pd.api.types.is_bool_dtype: 'boolean',
#         pd.api.types.is_datetime64_any_dtype: 'datetime64[ns]',
#     }
#     for check, dtype_str in dtype_mapping.items():
#         if check(dtype):
#             return dtype_str
#     return 'String'
import re
#data quickbooks
def flatten_json_to_dataframe_qs(data):
    try:
        rows = []

        def process_dict(d, current_row=None):
            """
            Process a dictionary or nested JSON into rows, keeping all keys in the same row.
            """
            if current_row is None:
                current_row = {}
            if isinstance(d, dict):
                for key, value in d.items():
                    if isinstance(value, dict):
                        # Recursively process nested dictionaries
                        process_dict(value, current_row)
                    elif isinstance(value, list):
                        # Process each item in the list
                        if value!=[]:
                            for item in value:
                                process_dict(item, current_row.copy())
                        else:
                           current_row[key] = None
                    else:
                        # Add key-value pair to the current row
                        current_row[key] = value
                rows.append(current_row)  # Add the processed row
            elif isinstance(d, list):
                for item in d:
                    process_dict(item, current_row.copy())
            else:
                # If `d` is neither dict nor list, treat it as a value
                current_row["value"] = d
                rows.append(current_row)

        def process(data):
            if isinstance(data, list): 
                if data!=[]: # If the root data is a list
                    for item in data:
                        process_dict(item)
                else:
                    process_dict(data)
            elif isinstance(data, dict):  # If the root data is a dictionary
                process_dict(data)
            else:
                raise ValueError("Input data must be a dictionary or a list.")

        # Start processing the data
        process(data)
        # Create a DataFrame from the processed rows
        df = pd.DataFrame(rows)
        df =df.drop_duplicates()
        return df

    except Exception as e:
        print(f"Error: {e}")
        return None






def flatten_json_to_dataframe(data):
    try:
        def flatten_dict(d, parent_key='', sep='.'):
            """
            Recursively flattens a dictionary. Nested keys are concatenated with the parent key using the specified separator.
            """
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            # Add dictionary elements in the list as new columns
                            items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                        else:
                            # Convert non-dict list elements to strings
                            items.append((f"{new_key}[{i}]", item))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        # Process root-level input
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    
                    flat_data =[flatten_dict(item) for item in value]
                else:
                    # print(data)
                    pass
                    # Flatten each list found in the dictionary
                    # for item in value:
                    #     flat_data = [flatten_dict(item)]
                        # if isinstance(item, dict):
                        #     flat_data.append(flatten_dict(item))  # Convert single dictionary into a list of one item
        elif isinstance(data, list):
            flat_data = [flatten_dict(item) for item in data]  # Flatten each item in the list
        else:
            raise ValueError("Input data must be a dictionary or a list of dictionaries.")
        
        # Convert flattened data to a DataFrame
        df = pd.DataFrame(flat_data)
        return df
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


from sqlalchemy import create_engine, inspect, MetaData, Table, text,insert

def get_ddl(cursor, database_type,database):

    try:
        ddl_statements = []
        tables = []

        match database_type.lower():
            case 'postgresql':
                cursor_data = cursor.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"))
                tables = [row[0] for row in cursor_data.fetchall()]

                for table in tables:
                    cursor_data1 = cursor.execute(text(f"SELECT column_name, data_type,is_nullable FROM information_schema.columns WHERE table_name = '{table}';"))
                    columns = cursor_data1.fetchall()
                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type('postgresql',col[1],col[2])}"  for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case 'mysql':
                cursor_data = cursor.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in cursor_data.fetchall()]

                for table in tables:
                    cursor_data1 = cursor.execute(text(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = `{table}` ;"))
                    columns = cursor_data1.fetchall()
                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type('mysql',col[1],col[2])}" for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case 'oracle':
                cursor_data = cursor.execute(text("SELECT table_name FROM user_tables;"))
                tables = [row[0] for row in cursor_data.fetchall()]

                for table in tables:
                    cursor_data1 = cursor.execute(text(f"SELECT COLUMN_NAME, DATA_TYPE, NULLABLE FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{table}';"))
                    columns = cursor_data1.fetchall()
                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type('oracle',col[1],col[2])}" for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case 'snowflake':
                cursor_data = cursor.execute(text("SHOW TABLES;"))
                tables = [row[1] for row in cursor_data.fetchall()]

                for table in tables:
                    cursor_data1 = cursor.execute(text(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';"))
                    columns = cursor_data1.fetchall()
                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type('snowflake',col[1],col[2])}" for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case 'sqlite':
                try:
                    cursor_data = cursor.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                    # a = cursor.execute(text('select * from quickbooks;'))
                except Exception as e:
                    print(e)
                # for i in cursor_data.fetchall():
                #     print('da',i)
                tables = [row[0] for row in cursor_data.fetchall()]
                for table in tables:
                    
                    cursor_data1 = cursor.execute(text(f"PRAGMA table_info({table});"))
                    columns = cursor_data1.fetchall()

                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[1]}\" {convert_to_clickhouse_type('sqlite',col[2],col[3])}" for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case 'microsoftsqlserver':
                cursor_data = cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
                tables = [row[0] for row in cursor_data.fetchall()]

                for table in tables:
                    cursor_data1 = cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}';")
                    columns = cursor_data1.fetchall()
                    ddl = f"CREATE TABLE \"{database}\".\"{table}\" (\n"
                    ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type('microsoftsqlserver',col[1],col[2])}" for col in columns])
                    ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"
                    ddl_statements.append((table, ddl))

            case _:
                raise ValueError(f"Unsupported database type: {database_type}")

        return {'tables': tables, 'ddl': ddl_statements}

    except Exception as e:
        return {'tables': [], 'ddl': []}
def get_postgresql_ddl(cursor):

    try:
        cursor1 = cursor.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
    
        tables = [row[0] for row in cursor1.fetchall()]
        ddl_statements = []
        for table in tables:
            # table_name = table[0]
            cursor2=cursor.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';"))
            columns = cursor2.fetchall()
            ddl = f"CREATE TABLE \"{table}\" (\n"
            ddl += ",\n".join([f"    \"{col[0]}\" {convert_to_clickhouse_type(col[1])}" for col in columns])
            ddl += "\n) ENGINE = MergeTree() ORDER BY tuple();"  
            ddl_statements.append((table, ddl))
        
        return {'tables':tables,'ddl':ddl_statements}
    except Exception as e:
        print(str(e))

def create_clickhouse_tables(client, ddl_statements):
    """
    Create ClickHouse tables based on PostgreSQL DDL statements.
    """
    for table_name, ddl in ddl_statements:
       
        try:
            client.command(ddl.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS"))
            # client.command(ddl)
        except Exception as e:
            print(f"Error creating table '{table_name}': {str(e)}")
    return {'status':200}

import time


def migrate_table(pg_cursor, clickhouse_client, table_name, database,batch_size=10000):
    load_data_to_clickhouse(pg_cursor, clickhouse_client, table_name, database)


from concurrent.futures import ProcessPoolExecutor



def load_data_to_clickhouse(pg_cursor, table_name, database):
    """
    Fetch data from PostgreSQL and load it into ClickHouse in batches.
    """
    try:
        pg_cursor1 = pg_cursor.execute(text(f"SELECT * FROM \"{table_name}\";"))
        columns =[f'\"{desc[0]}\"' for desc in pg_cursor1.cursor.description]
        while True:
            rows = pg_cursor1.fetchmany(100000)
            
            if not rows:
                break
            insert_batch(rows,table_name,database,columns)

        # with ProcessPoolExecutor(max_workers=4) as executor:
        #     while True:
        #         rows = pg_cursor.fetchmany(100000)
        #         if not rows:
        #             break
        #         executor.submit(insert_batch, rows,table_name,database,columns)

    except Exception as e:
        print(f"Error loading data into ClickHouse for table '{table_name}': {str(e)}")

def clean_data(row, column_types):
    cleaned_row = []
    for value, col_type in zip(row, column_types):
        if value is None:  # Handle NULL values
            cleaned_row.append(None if "Nullable" in col_type else "")
        elif col_type.startswith("Int"):
            cleaned_row.append(int(value))
        elif col_type.startswith("Float"):
            cleaned_row.append(float(value))
        elif col_type.startswith("Decimal"):
            cleaned_row.append(float(value))  # Ensure proper precision/scale
        elif col_type == "Date":
            cleaned_row.append(str(value))  # Format date as 'YYYY-MM-DD'
        elif col_type == "DateTime":
            cleaned_row.append(str(value))  # Format datetime as 'YYYY-MM-DD HH:MM:SS'
        else:
            cleaned_row.append(str(value))
    return cleaned_row

def escape_single_quotes(value):
    """Escapes single quotes in a string value for SQL compatibility."""
    if isinstance(value, str):  # Only escape if it's a string
        return value.replace("'", "")  # Replace single quotes with double single quotes
    return str(value)  # Return the value as is if it's not a string


def process_values_for_insertion(rows):
    """Processes rows to escape single quotes in string values before insertion."""
    processed_rows = []
    for row in rows:
        processed_row = [escape_single_quotes(value) for value in row]  # Escape single quotes in each value
        processed_rows.append(tuple(processed_row))  # Ensure each row is a tuple
    return processed_rows
from multiprocessing import Pool


integer_list=['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double','int64','int32','float64','float32','nullable(int64)', 'nullable(int32)', 'nullable(uint8)', 
    'nullable(float(64))','int8','int16','int32','int64','float32','float16','float64','decimal(38,10)','decimal(12,2)','uuid','nullable(int8)','nullable(int16)','nullable(int32)','nullable(int64)','nullable(float32)','nullable(float16)','nullable(float64)','nullable(decimal(38,10)','nullable(decimal(12,2)']
char_list=['varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying','string','str','nullable(varchar)', 'nullable(bp char)', 'nullable(text)', 
    'nullable(varchar2)', 'nullable(NVchar2)', 
    'nullable(long)', 'nullable(char)', 'nullable(Nchar)', 
    'nullable(character varying)', 'nullable(string)','string','nullable(string)','array(string)','nullable(array(string))']
bool_list=['bool','boolean','nullable(bool)', 'nullable(boolean)','uint8']
date_list=['date','time','datetime','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone','timestamptz','nullable(date)', 'nullable(time)', 'nullable(datetime)', 
    'nullable(timestamp)', 
    'nullable(timestamp with time zone)', 
    'nullable(timestamp without time zone)', 
    'nullable(timezone)', 'nullable(time zone)', 'nullable(timestamptz)', 
    'nullable(datetime)','datetime64','datetime32','date32','nullable(date32)','nullable(datetime64)','nullable(datetime32)','date','datetime','time','datetime64','datetime32','date32','nullable(date)','nullable(time)','nullable(datetime64)','nullable(datetime32)','nullable(date32)'] 


import gc
def decode_memoryview(value):
    if isinstance(value, memoryview):
        return value.tobytes().decode('utf-8', errors='ignore')  # Adjust encoding as per your data
    return value

def insert_batch(rows,table_name,database,columns):
        try:
            clickhouse_1 = Clickhouse(database)
            client = clickhouse_1.client
            df = pd.DataFrame(rows)
            for index, col in enumerate(df.columns):
                if any(isinstance(x, memoryview) for x in df[col]):
                    df[col] = df[col].apply(decode_memoryview)
                elif columns[index] in integer_list:
                    df[col] = df[col].astype(int)  # Convert to integer
                elif columns[index] in char_list:
                    df[col] = df[col].astype(str)  # Convert to string
                # elif columns[index] in date_list:
                #     df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime
                elif columns[index] in bool_list:  # Assuming you have a list of boolean columns
                    df[col] = df[col].astype(bool)

# Convert to list of tuples
            # rows_to_insert = [tuple(x) for x in df.to_numpy()]

            client.insert_df(table_name, df)
        except Exception as e:
            print(f'sa;{table_name}',e)
        finally:
            del rows
            del df
            gc.collect()
            if 'client' in locals():
                client.close() 

# def insert_batches_to_clickhouse(table_name,database,rows,columns,source_cursor):
#     try:
#         insert_batch(rows,table_name,database,columns)
        
#         # max_staff = get_max_workers()
#         # batch_size = 100000
#         # batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]
#         # with Pool(4) as pool:  # Adjust number of processes
#         #     pool.starmap(insert_batch, [(batch, table_name, database, columns) for batch in batches])
#         # # with ThreadPoolExecutor() as executor:  
#         # #     futures = [
#         # #         executor.submit(insert_batch, rows,columns)
#         # #     ]
#         # #     for future in futures:
#         # #         future.result()  

#         # end_time = time.time()
#     except Exception as e:
#         print(e)
import json
class Clickhouse():
    def __init__(self,database='default'):
        # try:
        self.client = clickhouse_connect.get_client(host = settings.clickhouse_host,port=settings.clickhouse_port,username = settings.clickhouse_username,password = settings.clickhouse_password,database=database,
        settings={'date_time_input_format':'best_effort','input_format_null_as_default': 1,'async_insert': 1,
             'wait_for_async_insert':1,'input_format_try_infer_dates': 1,
            'input_format_try_infer_datetimes': 1,
             'input_format_try_infer_datetimes_only_datetime64':1,
             'input_format_csv_use_best_effort_in_schema_inference': 1,
            'enable_extended_results_for_datetime_functions': 1,
            'receive_timeout': 600,  # in seconds
            'http_receive_timeout': 60,  # in seconds
            'receive_data_timeout_ms': 3000,  # in milliseconds
            'async_insert_busy_timeout_ms': 2000,
             'insert_null_as_default':1 })
        # clickhouse_client = clickhouse_connect.get_client(host='your_clickhouse_host', username='your_username', password='your_password', )
        # self.clickhouse_url = "clickhouse+http://default:@localhost:8123/default"
        # registry.register("clickhouse", "clickhouse_sqlalchemy.dialect", "ClickHouseDialect")
        if settings.DATABASES['default']['NAME']=='insightapps_dev':
            self.clickhouse_url = f'clickhouse+http://{settings.clickhouse_username}:{settings.clickhouse_password}@{settings.clickhouse_host}:{settings.clickhouse_port}/{database}?protocol=https'
        else:
            self.clickhouse_url = f'clickhouse+http://{settings.clickhouse_username}:{settings.clickhouse_password}@{settings.clickhouse_host}:{settings.clickhouse_port}/{database}'
        self.engine = create_engine(self.clickhouse_url,connect_args={
          'verify': False,
         'settings': {'date_time_input_format':'best_effort','input_format_null_as_default': 1,'async_insert': 1,
                    'wait_for_async_insert':1,'input_format_try_infer_dates': 1,
             'input_format_try_infer_datetimes': 1,
             'input_format_try_infer_datetimes_only_datetime64':1,'input_format_csv_use_best_effort_in_schema_inference': 1,
             'enable_extended_results_for_datetime_functions': 1,
             'receive_timeout': 600,  # in seconds
            'http_receive_timeout': 60,  # in seconds
            'receive_data_timeout_ms': 3000,  # in milliseconds
            'async_insert_busy_timeout_ms': 2000,'insert_null_as_default':1 }})
        self.cursor = self.engine.connect()
        # except Exception as e:
        #     return {"status":400,"message":"Connection Error"}

    def Postgres_clickhouse_migration(self,hostname,port,source_database,password,database,username,table):
        try:
            # print(hostname,port,source_database,password,database)
            # cursor_data = cursor.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"))
            # tables = [row[0] for row in cursor_data.fetchall()]



            # with ThreadPoolExecutor(max_workers=4) as executor:
            #     futures = [
            #         executor.submit(process_table, table, source_databasedatabase, hostname, port, a, username, password, self.client)
            #         for table in tables
            #     ]
            #     # Wait for all tasks to complete
            #     for future in futures:
            #         try:
            #             future.result()
            #         except Exception as e:
            #             print(f"Exception in thread: {e}")
            # return {'status': 200}
            # for table in tables:

            click = Clickhouse()
            client = click.client
            create_query = f"""CREATE OR REPLACE TABLE  \"{database}\".\"{table}\"
            ENGINE = MergeTree
            ORDER BY () EMPTY AS
            SELECT * FROM postgresql('{hostname}:{port}', '{source_database}', '{table}', '{username}', '{password}')"""
            client.command(create_query)
            insert_query = f""" INSERT INTO \"{database}\".\"{table}\" SELECT *
                                FROM postgresql('{hostname}:{port}', '{source_database}', '{table}', '{username}', '{password}')"""
            client.command(insert_query)
        except Exception as e:
            print(str(e))
            return {'status':400,'message':str(e)}
            

        


    def migrate_database_to_clickhouse(self,source_cursor,conn_type,database,username, password, actual_database, hostname,port,service_name,parameter,server_path):

        if parameter.lower() == 'postgresql':
            cursor_data = source_cursor.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"))
            tables = [row[0] for row in cursor_data.fetchall()]
            # postgres_insertion = self.Postgres_clickhouse_migration(hostname,port,actual_database,password,database,username,self.client,tables)
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(self.Postgres_clickhouse_migration, hostname,port,actual_database,password,database,username,table)
                    for table in tables
                ]
                # Wait for all tasks to complete
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Exception in thread: {e}")
            return {'status': 200}
        else:
            ddl_data = get_ddl(source_cursor,conn_type.lower(),database)
            ddl_statements = ddl_data['ddl']
            table_names = ddl_data['tables']
            try:
                if not table_names:
                    return {'status':200}
                create_tables = create_clickhouse_tables(self.client, ddl_statements)
                if create_tables['status'] ==200:
                    del ddl_data
                    del ddl_statements
            


            # with ThreadPoolExecutor(max_workers=4) as executor:  
            #     futures = [
            #         executor.submit(load_data_to_clickhouse, source_cursor,table_name,database)
            #         for table_name in table_names
            #     ]
            #     for future in futures:
            #         future.result()  
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    for table_name in table_names:
                        future = executor.submit(load_data_to_clickhouse, source_cursor, table_name, database)
                        futures.append(future)
                        if len(futures) >= 4:
                            for f in futures:
                                f.result()
                            futures.clear()
                    for f in futures:
                        f.result()

                return {'status':200}

            except Exception as e:
                return {'status':400,'message':str(e)}
    

    def insert_into_clickhouse(self, file, file_type,file_binary_data):
        try:
            # file_data = f'media/{file}'
            file_name, file_extension = os.path.splitext(os.path.basename(file))
            file_name = file_name.replace(' ','_').replace('&','')
            # Create database if it doesn't exist
            self.client.query(f'CREATE DATABASE IF NOT EXISTS "{file}"')


            if file_type.lower() == 'csv' and file_extension.lower() == '.csv':
                return self._insert_csv(file,file_binary_data)
            
            elif file_type.lower() == 'excel' and (file_extension.lower() in ['.xls', '.xlsx']):
                return self._insert_excel(file_binary_data, file)

            else:
                return {'status': 400, 'message': 'Unsupported file type.'}

        except Exception as e:
            return {'status': 400, 'message': str(e).splitlines()[0]}   

    def _insert_csv(self,file_name,file_used_data):
        try:
            # binary_buffer = io.BytesIO(file_used_data.read())
            # dataframe = pd.read_csv(binary_buffer)
            # table_name = f"""\"{file_name}\".\"{file_name}\""""
            # result  =insert_df_into_clickhouse(table_name,dataframe)

            try:
                file_used_data.seek(0)
            except:
                pass
            binary_buffer = io.BytesIO(file_used_data.read())
            dataframe = pd.read_csv(binary_buffer,keep_default_na=False)
            table,table_ext = os.path.splitext(os.path.basename(file_name))
            table_name = f"""\"{file_name}\".\"{table}\""""
            result  =insert_df_into_clickhouse(table_name,dataframe)

            return {'status':200,'message':'sucess'}

        except Exception as e:
            return {'status':400,'message':e}

        

    def _insert_excel(self, file_data, file_name):
        try:
            
            xls = pd.ExcelFile(file_data)
            
            # Prepare a list of tasks for parallel processing
            tasks = [(file_name,sheet, xls.parse(sheet,keep_default_na=False).fillna(value='NA'))  for sheet in xls.sheet_names ]
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(executor.map(_process_sheet, tasks))

            xls.close()
            
            # Collect results and check for errors
            for result in results:
                if result['status'] != 200:
                    return result

            return {'status': 200, 'message': 'Excel File Tables Inserted'}

        except Exception as e:
            return {'status': 400, 'message': str(e).splitlines()[0]}

    

    # Ensure ClickHouse server settings are optimized
    def optimize_clickhouse_settings(self):
        # Example settings to optimize ClickHouse performance
        settings_query = """
        SET max_insert_block_size = 1048576; -- Increase max insert block size
        SET max_memory_usage = 10000000000; -- Set memory usage limit (10 GB)
        SET min_bytes_to_use_direct_io = 1048576; -- Use direct IO for large files
        """
        self.client.query(settings_query)

    
    def Clickhouse_query(self,query):
        try:
            query_result = self.client.query(query)
        except Exception as e:
            main_error_line = str(e).splitlines()[0]
            return_response = {
                'status':400,
                'message':main_error_line
            }
            return return_response
        return_response = {
            'status':200,
            'columns':query_result.column_names,
            'rows':query_result.result_rows
            }
    
    def engine_dispose(self):
        self.engine.dispose(close=True)

    def delete_database(self,file_name):
        try: 
            # delete_query =f'Drop DATABASE IF Exists{file_name}
            delete_query =f'Drop DATABASE IF Exists \"{file_name}\"'
            self.client.query(delete_query)
            return {'status':200,'message':'Database Dropped'}
        except Exception as e:
            return {'status':400,'message':e}

    def get_database_details(self,file_name):  
        query = f"""
        SELECT 
            table AS table_name,
            name AS column_name,
            type AS data_type
        FROM 
            system.columns
        WHERE 
            database = '{file_name}'
        ORDER BY 
            table_name, column_name
        """
        result = self.client.query(query).result_rows
        
        

        # Group columns by table name
        tables = {}
        for table_name, column_name, data_type in result:
            if table_name not in tables:
                tables[table_name] = []
            tables[table_name].append({"column": column_name, "datatypes": data_type})

        # Append each table structure to the response
        response = []
        for table_name, columns in tables.items():
            response.append({
                "schema": file_name,
                "table": table_name,
                "columns": columns
            })
        result1 = [{'status': 200}, *response]
        # Convert to JSON format
        return result1
    
    def json_to_table(self,tables_list,user_token,id,database,parameter):
        from quickbooks.views import quickbooks_query_data
        from quickbooks.salesforce_endpoints import salesforce_query_data
        from quickbooks import connectwise,halops,shopify,models
        from dashboard import columns_extract,models as dsh_models
        try:
            for table in tables_list:
                if parameter.lower() == 'quickbooks':
                    data  = quickbooks_query_data(id,user_token,table)
                    print(data)
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe_qs(data['data'])
                    else:
                        continue
                elif parameter.lower() == 'salesforce':
                    print("salesforce")
                    data = salesforce_query_data(id,user_token,table)
                    print(data)
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe_qs(data['data'])
                    else:
                        continue
                elif parameter.lower() =='connectwise':
                    data = connectwise.connectwise_data(table,id)
                    print(data)
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe(data['data'])
                    else:
                        continue
                elif parameter.lower() =='halops':
                    data = halops.halops_data(table,id)
                    print(data)
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe(data['data'])
                    else:
                        continue
                elif parameter=='mongodb':
                    data = columns_extract.mongo_connection_data(id,table)
                    print(data)
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe(data['data'])
                    else:
                        continue
                elif parameter=='shopify':
                    data = shopify.shopify_data(id,table)
                    print(data)
                    # a = json.dumps(data, indent=4)
                    # with open(table+'.json','w') as outfile:
                    #     outfile.write(a)
                    
                    if data['status']==200:
                        dataframe = flatten_json_to_dataframe_qs(data['data'])
                    else:
                        continue
                columns_data = []
                for i in dataframe.columns:
                    if i.lower() in columns_data:
                        count_server = columns_data.count(i.lower())
                        # a = a.rename({i:f'{i}_{count_server+1}'})
                        dataframe.rename(columns={i:f'{i}_{count_server+1}'}, inplace=True)
                    else:
                        columns_data.append(i.lower())
                table=str(table).replace('/','_')
                table_name = f"\"{database}\".\"{table}\""
                task = [(table_name,dataframe)]
                if dataframe.empty:
                    pass
                else:
                    with concurrent.futures.ProcessPoolExecutor() as executor:
                        futures = [executor.submit(insert_df_into_clickhouse, param1, param2) for param1, param2 in task]
                        # results = list(executor.map(lambda t: insert_df_into_clickhouse(*t), task))
                    # for result in results:
                    #     if result['status'] != 200:
                    #         return result
                    for future in concurrent.futures.as_completed(futures):
                        # param1, param2 = futures[future]
                        try:
                            result_data = future.result()
                            if result_data['status'] != 200:
                                return result_data
                        except Exception as e:
                            pass
                # results = [future.result() for future in concurrent.futures.as_completed(futures)]

            return {'status': 200, 'message': 'Quickboooks Table inserted'}

        except Exception as e:
            print('e')
            return {'status': 400, 'message': str(e).splitlines()[0]}

            # creation = self.insert_df_into_clickhouse(table,dataframe)
from collections import Counter



from dateutil import parser

def infer_date_format(date_string):
    try:
        parsed_date = parser.parse(date_string)
        return str(parsed_date)  # Returns the parsed date in ISO format
    except ValueError:
        return None


def detect_date_format(date_string):
    if re.match(r'\d{4}-\d{2}-\d{2}', date_string):
        return "YYYY-MM-DD"
    elif re.match(r'\d{2}/\d{2}/\d{4}', date_string):
        return "DD/MM/YYYY"
    elif re.match(r'\d{2}-\d{2}-\d{4}', date_string):
        return "MM-DD-YYYY"
    elif re.match(r'\w+ \d{1,2}, \d{4}', date_string):
        return "Month DD, YYYY"
    elif re.match(r'\d{1,2} \w+ \d{4}', date_string):
        return "DD Month YYYY"
    elif re.match(r'\d{4}/\d{2}/\d{2}', date_string):
        return "YYYY/MM/DD"
    elif re.match(r'\d{2}\.\d{2}\.\d{4}', date_string):
        return "MM.DD.YYYY"
    elif re.match(r'\d{8}', date_string):
        return "YYYYMMDD"
    elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_string):
        return "MDY or DMY"
    elif re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([-+]\d{2}:\d{2}|Z)', date_string):
        return "ISO 8601 Datetime with Timezone"
    elif re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', date_string):
        return "DD/MM/YYYY HH:MM"
    elif re.match(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}', date_string):
        return "MM-DD-YYYY HH:MM"
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_string):
        return "YYYY-MM-DD HH:MM:SS"
    elif re.match(r'([1-12]:[0-5][0-9] (AM|PM|am|pm))', date_string):
        return "HH:MM AM/PM"
    elif re.match(r'\d{1,2} \w+ \d{4} \d{2}:\d{2}', date_string):
        return "DD Month YYYY HH:MM"
    return str(date_string) if pd.notna(date_string) else date_string

from datetime import datetime

def is_date_column(series):
    """
    Returns True if the column likely contains date strings.
    """
    # Check if the column is of object type
    if series.dtype == 'object':
        # Verify if the column is not fully numeric
        if not pd.to_numeric(series[series.notna()], errors='coerce').notna().all():
            # Attempt to convert to datetime and check if any conversion was successful
            converted = pd.to_datetime(series, errors='coerce')
            return converted.notna().any()  # Return True if any entry is a valid date

    return False

def convert_datetime_columns(df):

    potential_date_columns = [col for col in df.columns if is_date_column(df[col])]     



    for column in potential_date_columns:
        try:
                # Use apply with dateutil's parse to convert the column
                # df[column] = df[column].apply(lambda x: parser.parse(x) if pd.notnull(x) else x)
            try:
                df[column] = df[column].apply(
                    lambda x: parser.parse(x) if pd.notnull(x) and isinstance(x, str) else  None)
                if pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column] = df[column].dt.tz_localize(None)
                # default_datetime = datetime(1970, 1, 1)  # Unix epoch start
                # df[column] = df[column].fillna(default_datetime)
                # df[column] = df[column].where(pd.notnull(df[column]), None)
                # df[column] =df[column].where(pd.NaT(df[column]),None)
                df[column] = pd.to_datetime(df[column],errors = 'coerce')
                df[column] = df[column].apply(lambda x: pd.Timestamp(x) if pd.notna(x) and not pd.NaT(x) else None)
            except Exception as e:
                print(e)
                continue
        except Exception as e:
            print(e)
            # If conversion fails, print an error message (optional) and skip the column
            continue
    return df


# def map_dtypes_to_clickhouse(df):
#     try:
#         type_mapping = {
#             'object': 'String',
#             'int64': 'Int64',
#             'float64': 'Float64',
#             'bool': 'Bool',
#             'datetime64[ns]': "DateTime64",  # Handle datetime
#         }
#         clickhouse_schema = []
        
#         for column in df.columns:
#             dtype = str(df[column].dtype)
#             if dtype in type_mapping:
#                 if df[column].isnull().any():
#                     clickhouse_schema.append(f"`{column}` Nullable({type_mapping[dtype]}) DEFAULT '1970-01-01 00:00:00'" if dtype =='datetime64[ns]' else f"`{column}` Nullable({type_mapping[dtype]})")
#                 else:
#                     clickhouse_schema.append(f"`{column}` {type_mapping[dtype]}")
#             else:
#                 raise ValueError(f"Unsupported dtypes: {dtype} for column: {column}")

#         return ", ".join(clickhouse_schema)
#     except Exception as e:
#         print(e)




def map_dtypes_to_clickhouse(df):
    try:
        type_mapping = {

            'String':'String',
            'object': 'String',
            'int64': 'Int64',
            'UInt64':'Int64',
            'float64': 'Float64',
            'bool': 'Bool',
            'datetime64[ns]': "DateTime64",
            'datetime64[ns, tzoffset(None, -28800)]':"DateTime64"  # Handle datetime
        }
        clickhouse_schema = []
        for column in df.columns:
            dtype = str(df[column].dtype)

            if df[column].isnull().any():
                clickhouse_schema.append(f"`{column}` Nullable(DateTime64) DEFAULT '1970-01-01 00:00:00'" if 'datetime' in  str(dtype.lower()) else f"`{column}` Nullable({type_mapping[dtype]})")
            else:
                clickhouse_schema.append(f"`{column}` DateTime64 DEFAULT '1970-01-01 00:00:00'" if 'datetime' in  str(dtype.lower()) else f"`{column}` {type_mapping[dtype]}")
            # else:
            #     raise ValueError(f"Unsupported dtypes: {dtype} for column: {column}")

        return ", ".join(clickhouse_schema)
    except Exception as e:
        print(e)




# def map_dtypes_to_clickhouse(df):
#     type_mapping = {
#         'object': 'String',
#         'int64': 'Int64',
#         'float64': 'Float64',
#         'bool': 'Bool',
#         'datetime64[ns]': 'DateTime64',  # Handle datetime
#     }
#     clickhouse_schema = []
    
#     for column in df.columns:
#         dtype = str(df[column].dtype)
#         if dtype in type_mapping:
#             clickhouse_schema.append(f"`{column}` Nullable({type_mapping[dtype]})")
#         else:
#             raise ValueError(f"Unsupported dtypes: {dtype} for column: {column}")

#     return ", ".join(clickhouse_schema)



def clean_dataframe(df):
    # Convert NaNs to None for proper null handling

    # Convert object types that are supposed to be numeric and ensure string types
    for col in df.select_dtypes(['object']).columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Converts and sets non-convertible values to NaN
        except ValueError as e:
            pass

    # Convert all remaining numbers to strings (if needed)
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].fillna('').astype(str)
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].replace({pd.NaT: None})
            df[col] = df[col].fillna(None,inplace=True)
            

    return df

def convert_to_clickhouse_type(conn_type, col,nullable):
    """
    Maps a database column type to the corresponding ClickHouse column type.

    Parameters:
        conn_type (str): The source database type (e.g., 'mysql', 'postgresql', 'sqlite', etc.).
        col (str): The column type to map.

    """
    # Define mappings for different database types to ClickHouse types
    db_to_clickhouse_mappings = {
        "mysql": {
            "tinyint": "Int8",
            "smallint": "Int16",
            "mediumint": "Int32",
            "int": "Int32",
            "integer": "Int32",
            "bigint": "Int64",
            "float": "Float32",
            "double": "Float64",
            "decimal": "Decimal(38, 10)",
            "char": "String",
            "varchar": "String",
            "text": "String",
            "mediumtext": "String",
            "longtext": "String",
            "json": "String",
            "date": "Date",
            "datetime": "DateTime",
            "timestamp": "DateTime",
            "time": "Time",
            "enum": "String",
            "set": "String",
            "blob": "String"
        },
        "postgresql": {
            "smallint": "Int16",
            "integer": "Int32",
            "bigint": "Int64",
            "decimal": "Decimal(38, 10)",
            "numeric": "Decimal(38, 10)",
            "real": "Float32",
            "double precision": "Float64",
            "boolean": "bool",
            "bool": "bool",
            "char": "String",
            "varchar": "String",
            "text": "String",
            "json": "String",
            "jsonb": "String",
            "uuid": "UUID",
            "bytea": "String",
            "xml": "String",
            "inet": "String",
            "cidr": "String",
            "macaddr": "String",
            "date": "Date",
            "timestamp":'DateTime64',
            "timestamp without time zone": "DateTime64",
            "timestamp with time zone": "DateTime64",
            "time without time zone": "Time",
            "time with time zone": "Time",
            "array": "Array(String)",
            "money": "Decimal(12, 2)"
        },
        "oracle": {
            "number": "Decimal(38, 10)",
            "float": "Float32",
            "binary_float": "Float32",
            "binary_double": "Float64",
            "char": "String",
            "varchar2": "String",
            "nchar": "String",
            "nvarchar2": "String",
            "clob": "String",
            "blob": "String",
            "nclob": "String",
            "date": "Date",
            "timestamp": "DateTime",
            "timestamp with time zone": "DateTime64",
            "timestamp with local time zone": "DateTime64",
            "raw": "String"
        },
        "sqlite": {
            "integer": "Float64",
            "real": "Float64",
            "text": "String",
            "blob": "String",
            "numeric": "Decimal(38, 10)",
            "date": "Date",
            "datetime": "DateTime64",
            "decimal":"Float64"
        },
        "snowflake": {
            "number": "Decimal(38, 10)",
            "integer": "Int32",
            "bigint": "Int64",
            "float": "Float64",
            "real": "Float32",
            "double": "Float64",
            "decimal": "Decimal(38, 10)",
            "string": "String",
            "text": "String",
            "boolean": "bool",
            "date": "Date",
            "timestamp": "DateTime",
            "timestamp_ntz": "DateTime",
            "timestamp_ltz": "DateTime64",
            "timestamp_tz": "DateTime64",
            "variant": "String",
            "object": "String",
            "array": "Array(String)"
        }
    }

    # Get the mapping dictionary for the specified database type
    mapping = db_to_clickhouse_mappings.get(conn_type.lower())

    # Return the mapped type or default to Nullable(String)
    if mapping:
        data_type = mapping.get(col.lower(), "String")
        
        if str(nullable).lower() in ('0', 'false', 'no', 'none', False):
            data_type = data_type
        else:
            data_type =  f'Nullable({data_type})'
        if data_type in date_list:
            data_type += "DEFAULT '1970-01-01 00:00:00"
        return data_type
    else:
        raise ValueError(f"Unsupported connection type: {conn_type}")

def insert_df_into_clickhouse(table_name,dataframe):
    try:

        dataframe = convert_datetime_columns(dataframe)
        schema = map_dtypes_to_clickhouse(dataframe)
    
        create_table_query = f"""
        CREATE or Replace Table {table_name} (

            {schema}
        ) ENGINE = MergeTree()
        ORDER BY tuple()
            """
        # print(create_table_query)
        
        
        click = Clickhouse()
        # Execute the CREATE TABLE statement
        click.client.command(create_table_query)
        for col in dataframe.columns:
            if dataframe[col].dtype == 'float64':
                dataframe[col] = dataframe[col].astype(float)
                # dataframe[col] = dataframe[col].where(pd.notnull(dataframe[col]),None)
            elif dataframe[col].dtype == 'int64':
                dataframe[col] = dataframe[col].astype(int)
                # dataframe[col] = dataframe[col].where(pd.notnull(dataframe[col]),None)
            elif pd.api.types.is_object_dtype(dataframe[col]):
                dataframe[col] = dataframe[col].astype(str)
                # dataframe[col] = dataframe[col].where(pd.notnull(dataframe[col]),None)
            # else:
            #     dataframe[col] = dataframe[col].where(pd.notnull(dataframe[col]),None)
            elif dataframe[col].dtype =='datetime64[ns]':
                default_timestamp = pd.Timestamp("1970-01-01 00:00:00") 
                dataframe[col] = dataframe[col].fillna(default_timestamp)


        try:
            dataframe = dataframe.replace([np.nan,pd.NaT ,np.inf, -np.inf,pd.NA], None)
            # dataframe = dataframe.applymap(lambda x: None if pd.isna(x) else x)
            click.client.insert_df(table_name, dataframe)
        except Exception as e:
            print(e)
            pass# Print DataFrame for debugging if needed
        # click.client.insert_df(table_name,dataframe)

        return {'status':200,'message':'sucess'}
    except Exception as e:
        return {'status':400,'error':str(e)}



def _process_sheet( task):
    try:
        file_name,sheet_name, dataframe = task
        if dataframe.empty:
            pass
        else:
            
            table_name = f'\"{file_name}\".\"{sheet_name}\"'
            result = insert_df_into_clickhouse(table_name,dataframe)
            if result['status'] !=200:
                return result
        return {'status':200,'message':'sucess'}
    except Exception as e:
        return {'status':400,'error':str(e)}






