from dashboard.columns_extract import server_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from sqlalchemy import text
from dashboard.models import QuerySets, ServerDetails, ServerType,SheetFilter_querysets
from .serializers import ChartCopilot,APIKEYServerialzer
from dashboard.Connections import table_name_from_query
import ast
import base64
import json
import requests
import re
from dashboard.models import UserProfile,UserRole,Role, FileDetails, FileType
from dashboard.views import test_token
from .models import GPTAPIKey
from dashboard.files import read_csv_file,read_excel_file,read_pdf_file,read_text_file
from dashboard.columns_extract import file_details


# Create your views here.
def validate_api_key(KEY):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{'role': 'user', 'content':"Say this is a test"}]
            # 'max_tokens':5
        }
    )
    if response.status_code == 200:
        return Response({'message': True}, status=status.HTTP_200_OK)
    elif response.status_code == 404:
        res = {'error': {'message': 'The model `gpt-3.5-turbo` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}
        return Response({'message': res['error']['message']}, status=status.HTTP_404_NOT_FOUND)
        
    elif response.status_code == 401:
        # res = {'error': {'message': 'Incorrect API key provided: "{KEY}". You can find your API key at https://platform.openai.com/account/api-keys.'.format(KEY), 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_api_key'}}
        return Response({'message': f"Incorrect API key provided: '{KEY}'. \n\n You can find your API key at https://platform.openai.com/account/api-keys."}, status=status.HTTP_401_UNAUTHORIZED)
    
class ValidateApiKeyView(CreateAPIView):
    serializer_class = APIKEYServerialzer
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            usertable=UserProfile.objects.get(id=tok1['user_id'])
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                
                api_key = serializer.validated_data['key']
                validation_response = validate_api_key(api_key)

                if validation_response.status_code == 200:
                    if not GPTAPIKey.objects.filter(added_by = usertable.id).exists() :
                        GPTAPIKey.objects.create(api_key=api_key,
                                                api_key_status=True,
                                                gpt_model = 'gpt-turbo-3.5-0125',
                                                added_by = usertable.id
                                                )
                        return Response({'message': True}, status=status.HTTP_200_OK)
                    return Response({'message':"API KEY Already Exists",
                                     "api_key" : GPTAPIKey.objects.get(added_by = usertable.id).api_key
                                     },status=status.HTTP_409_CONFLICT)
                return validation_response
            return Response({'message':"Serialzier Error"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(tok1,status=tok1['status'])
    
class GetServerTablesList(CreateAPIView):
    serializer_class = ChartCopilot
    
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            usertable=UserProfile.objects.get(id=tok1['user_id'])
            userrole = UserRole.objects.get(user_id = usertable.id)
            role = Role.objects.get(role_id = userrole.role_id)
            if userrole.role_id == 1 and GPTAPIKey.objects.filter(added_by = usertable.id):
                gpt = GPTAPIKey.objects.get(added_by = usertable.id)
                API_KEY  =gpt.api_key
            elif not userrole.role_id == 1 :
                gpt = GPTAPIKey.objects.get(added_by = role.created_by) 
                API_KEY  =gpt.api_key
            else:
                API_KEY=''

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():   
                query_set_id = serializer.validated_data['id']
                user_prompt = serializer.validated_data['prompt']
                a = validate_api_key(API_KEY)
                
                if a.status_code ==200:
                    pass
                elif a.status_code == 401:
                    return Response({'message': a.data}, status=status.HTTP_401_UNAUTHORIZED)
                elif a.status_code == 404:
                    return Response({'message':a.data},status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':"Please try again"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                if not QuerySets.objects.filter(queryset_id=query_set_id).exists():
                    return Response({'message': "Invalid QuerySet ID"}, status=status.HTTP_404_NOT_FOUND)
                
                qs = QuerySets.objects.get(queryset_id=query_set_id)
                
                is_file =False
                if FileDetails.objects.filter(id=qs.file_id).exists():
                    is_file = True
                    file=FileDetails.objects.get(id=qs.file_id)
                    fi_type=FileType.objects.get(id=file.file_type)
                    
                    if qs.is_custom_sql:
                        files_data =file_details(fi_type.file_type,file)
                        if files_data['status']==200:
                            engine=files_data['engine']
                            # cursor=files_data['cursor']
                            with engine.connect() as connection:
                                # Execute the custom SQL query
                                from sqlalchemy import text
                                result = connection.execute(text(qs.custom_query))
                                # Get column names
                                columns = result.keys()
                                # Fetch the result rows
                                rows = result.fetchall()
                                
                            # Prepare metadata correctly
                            meta_data = []
                            if rows:
                                for idx, column in enumerate(columns):
                                    meta_data.append({
                                        "column_name": column,
                                        # Use the index to access the value in the tuple
                                        "data_type": str(type(rows[0][idx]))  # Access using integer index, not column name
                                    })
                            meta_data = rewrite_datatypes_for_metadata(meta_data,API_KEY)
                            # Generate chart suggestions based on the fetched columns
                            final_res = get_gpt_chart_suggestions(meta_data, user_prompt, API_KEY)

                            if 'error' in final_res:
                                return Response({"message": final_res['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            
                        else:
                            return Response({"message":files_data['message']},status=files_data['status'])
                    else:                        
                        filename = re.sub(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', '', file.display_name)
                        
                        if fi_type.file_type=='EXCEL':
                            data = read_excel_file(file.source,filename,file.id)
                        elif fi_type.file_type=='CSV':
                            data = read_csv_file(file.source,filename,file.id)
                        elif fi_type.file_type=='PDF':
                            data = read_pdf_file(file.source,filename,file.id)
                        elif fi_type.file_type=='TEXT':
                            data = read_text_file(file.source,filename,file.id)
                        else:
                            return Response({'error': 'Unsupported file type/format'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        
                        # Get the table metadata
                        file_metadata = data["data"]["schemas"][0]["tables"][0]
                        file_metadata = rewrite_datatypes_for_metadata(file_metadata,API_KEY)

                        # Generate chart suggestions based on the fetched columns
                        final_res = get_gpt_chart_suggestions(file_metadata, user_prompt, API_KEY)

                        if 'error' in final_res:
                            return Response({"message": final_res['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                elif ServerDetails.objects.filter(id=qs.server_id):
                    sd = ServerDetails.objects.get(id=qs.server_id)
                    server_type = ServerType.objects.get(id=sd.server_type).server_type
                    
                    server_conn =server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,server_type.upper(),sd.database_path)
                    if server_conn['status'] != 200:
                        return Response(server_conn, status=server_conn['status'])
                    
                    engine = server_conn['engine']
                    cursor = server_conn['cursor']
                    db_type = server_type
                
                if is_file and not qs.is_custom_sql:
                    # Try to correct the format again with new suggestions
                    text = final_res['choices'][0]['message']['content']
                    data = json.loads(text)
                    formatted_data = correct_format(data)
                    if formatted_data['status'] == "error":
                        return Response({"message": "Error generating chart suggestions. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        data = formatted_data['data']
                elif is_file and qs.is_custom_sql:
                    # Try to correct the format again with new suggestions
                    text = final_res['choices'][0]['message']['content']
                    data = json.loads(text)
                    formatted_data = correct_format(data)
                    if formatted_data['status'] == "error":
                        return Response({"message": "Error generating chart suggestions. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        data = formatted_data['data']
                # Handle custom SQL logic
                elif not is_file and qs.is_custom_sql:
                    # Execute the custom SQL query
                    custom_sql = qs.custom_query  # Assuming there's a field `custom_sql` in QuerySets
                    try:
                        # Use the existing server connection logic
                        engine = server_conn['engine']
                        with engine.connect() as connection:
                            # Execute the custom SQL query
                            from sqlalchemy import text
                            result = connection.execute(text(custom_sql))
                            # Get column names
                            columns = result.keys()

                            # Fetch the result rows
                            rows = result.fetchall()
                            
                        # Prepare metadata correctly
                        meta_data = []
                        if rows:
                            for idx, column in enumerate(columns):
                                meta_data.append({
                                    "column_name": column,
                                    # Use the index to access the value in the tuple
                                    "data_type": str(type(rows[0][idx]))  # Access using integer index, not column name
                                })
                        else:
                            # Handle the case where there are no rows
                            for column in columns:
                                meta_data.append({
                                    "column_name": column,
                                    "data_type": "No data"
                                })
                        
                        # Generate chart suggestions based on the fetched columns
                        final_res = get_gpt_chart_suggestions(meta_data, user_prompt, API_KEY)

                        if 'error' in final_res:
                            return Response({"message": final_res['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                        # Try to correct the format again with new suggestions
                        text = final_res['choices'][0]['message']['content']
                        data = json.loads(text)
                        formatted_data = correct_format(data)
                        if formatted_data['status'] == "error":
                            return Response({"message": "Error generating chart suggestions. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            data = formatted_data['data']

                        # return Response({"data": chart_suggestions}, status=status.HTTP_200_OK)

                    except Exception as e:
                        return Response({"message": f"Error executing custom SQL: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # Create a list to store the results in schema.table_name format
                    tables_list = qs.table_names
                    tables_list = ast.literal_eval(tables_list)
                    tables = []

                    # Iterate through the list
                    for entry in tables_list:
                        if len(entry) == 2:
                            schema, table = entry
                        elif len(entry) == 3:
                            schema, table, _ = entry  # Ignore the alias part
                        else:
                            continue  # Skip entries that don't match the expected structure
                        tables.append(f"{schema}.{table}")
                    result = get_table_meta_data(engine, cursor, tables, db_type)
                    # Ensure `result['data']` is a string that can be parsed by `ast.literal_eval`
                    if isinstance(result, dict) and 'data' in result:
                        result_data_str = json.dumps(result['data'])
                        op = ast.literal_eval(result_data_str)
                    else:
                        return Response({"message": "Error fetching table metadata."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    if can_build_chart(op, user_prompt,API_KEY) != "YES":
                        return Response({
                            "data": "The question <b>{}</b> doesn't seem to match any of the keywords in the provided table metadata. <br><br>Could you please rephrase the question and ask again ?".format(user_prompt)
                        })
                    
                    # Initial attempt to correct the format
                    formatted_data = correct_format(op)
                    
                    if formatted_data['status'] == "error":
                        # Retry getting GPT chart suggestions if correct_format fails
                        final_res = get_gpt_chart_suggestions(op, user_prompt,API_KEY)
                        if 'error' in final_res:
                            return Response({"message": final_res['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                        # Try to correct the format again with new suggestions
                        text = final_res['choices'][0]['message']['content']
                        data = json.loads(text)
                        formatted_data = correct_format(data)
                        if formatted_data['status'] == "error":
                            return Response({"message": "Error generating chart suggestions. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            data = formatted_data['data']
                    else:
                        data = formatted_data['data']
                
                # column_type_map = map_columns_to_datatypes(op)
                # corrected_charts = validate_chart_data(data, column_type_map)
                    
                final_data = []
                for chart in data['charts']:
                    chart_type_lower = chart['chart_type'].lower()
                    
                    # Determine chart_id based on chart_type
                    if "bar" in chart_type_lower:
                        chart_id = 6
                    elif "line" in chart_type_lower:
                        chart_id = 13
                    elif "pie" in chart_type_lower:
                        chart_id = 24
                    elif "area" in chart_type_lower:
                        chart_id = 17
                    else:
                        chart_id = 1
                        
                    new_data = {
                        "chart_title": chart['chart_title'],
                        "chart_type": chart['chart_type'],
                        "database_id": qs.server_id,
                        "queryset_id": qs.queryset_id,
                        "col": chart['col'],
                        "row": chart['row'],
                        "filter_id": [],
                        "columns": [
                            {
                                "column": col[0],
                                "data_type": col[1]
                            } for col in chart['col']
                        ],
                        "rows": [
                            {
                                "column": row[0],
                                "type": row[2]
                            } for row in chart['row']
                        ],
                        "datasource_quertsetid": "",
                        "sheetfilter_querysets_id": "",
                        "chart_id":chart_id
                    }
                    final_data.append(new_data)
                return Response({"data": final_data})
            else:
                return Response({'message':"Queryset ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])

def correct_format(data):
    try:
        for chart in data['charts']:
            for row in chart['row']:
                if len(row) == 3 and row[1] in ["avg", "sum", "min", "max", "count"] and row[2] == "":
                    row[1], row[2] = "aggregate", row[1]
                elif len(row) == 2 and row[1] in ["avg", "sum", "min", "max", "count"]:
                    row.append(row[1])
                    row[1] = "aggregate"
        return {"status": "success", "data": data}
    except Exception:
        return {"status": "error"}
    
def decode_string(encoded_string):
    # Add padding if necessary
    padding_needed = len(encoded_string) % 4
    if padding_needed:
        encoded_string += '=' * (4 - padding_needed)
    
    try:
        # Decode the Base64 string
        decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        # Handle errors if decoding fails
        print(f"Decoding error: {e}")
        return str(e)

def fetch_tables_from_query(query):
    try:
        return table_name_from_query(query)
    except Exception as e:
        return str(e)

def get_table_meta_data(engine, cursor, tables_list, database_type, mongo_client=None):
    try:
        if database_type == 'SQLITE':
            tables = [entry.split('.')[1] if '.' in entry else entry for entry in tables_list]
            placeholders = ', '.join([f":table{i}" for i in range(len(tables))])
            params = {f'table{i}': table for i, table in enumerate(tables)}
        elif database_type =='MICROSOFTSQLSERVER':
            schema_table_list = [table.split('.') for table in tables_list]
            conditions = ' OR '.join(['(table_schema = ? AND table_name = ?)'] * len(schema_table_list))
            params = [item for sublist in schema_table_list for item in sublist]
        else:
            # Split tables_list into schema and table names
            schema_table_list = [table.split('.') for table in tables_list]
            placeholders = ', '.join([f"(:schema{i}, :table{i})" for i in range(len(schema_table_list))])
            params = {f'schema{i}': schema for i, (schema, table) in enumerate(schema_table_list)}
            params.update({f'table{i}': table for i, (schema, table) in enumerate(schema_table_list)})
        

        if database_type == 'POSTGRESQL':
            query = text(f'''SELECT table_schema, table_name, column_name, data_type
                             FROM information_schema.columns
                             WHERE (table_schema, table_name) IN ({placeholders})''')
        
        elif database_type == 'ORACLE':
            # Adjust schema and table name for Oracle
            params = {f'schema{i}': schema.upper() for i, (schema, table) in enumerate(schema_table_list)}
            params.update({f'table{i}': table.upper() for i, (schema, table) in enumerate(schema_table_list)})
            query = text(f'''SELECT owner AS table_schema, table_name, column_name, data_type
                             FROM all_tab_columns
                             WHERE (owner, table_name) IN ({placeholders})''')
        
        elif database_type == 'MICROSOFTSQLSERVER':
            # query = f'''SELECT table_schema, table_name, column_name, data_type
            #                  FROM INFORMATION_SCHEMA.COLUMNS
            #                  WHERE (table_schema, table_name) IN ({placeholders})'''
            query = f'''SELECT table_schema, table_name, column_name, data_type
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE {conditions}'''
        elif database_type == 'MYSQL':
            query = text(f'''SELECT table_schema, table_name, column_name, data_type
                             FROM information_schema.columns
                             WHERE (table_schema, table_name) IN ({placeholders})''')
        
        elif database_type == 'SQLITE':
            query = text(f'''SELECT name AS table_name, sql
                             FROM sqlite_master
                             WHERE type='table' AND name IN ({placeholders})''')
            with engine.connect() as connection:
                result = connection.execute(query, params)
                tables_info = result.fetchall()
                meta_data = []
                for table in tables_info:
                    table_name, create_sql = table
                    column_definitions = re.search(r'\((.*)\)', create_sql, re.DOTALL).group(1)
                    columns_info = [col.strip() for col in column_definitions.split(',')]
                    for col in columns_info:
                        col_parts = col.split()
                        column_name = col_parts[0].strip('"')
                        data_type = col_parts[1]
                        meta_data.append({"table_name": table_name, "column_name": column_name, "data_type": data_type})
                return {"data": meta_data}
        else:
            return "Unsupported Database Type"

        if database_type == 'MICROSOFTSQLSERVER':
            # Use pyodbc with dynamically constructed query
            query_str = query
            cursor.execute(query_str, params)
            rows = cursor.fetchall()
            meta_data = [{"table_schema": row[0], "table_name": row[1], "column_name": row[2], "data_type": row[3]} for row in rows]
            return {"data": meta_data}
            
        with engine.connect() as connection:
            result = connection.execute(query, params)
            rows = result.fetchall()
            meta_data = [{"table_schema": row[0], "table_name": row[1], "column_name": row[2], "data_type": row[3]} for row in rows]
            return {"data": meta_data}

    except Exception as e:
        return str(e)


format_response = """{
    # use this keys INTEGER, VARCHAR, BOOLEAN, TIMESTAMPTZ for "datatype"
    # INTEGER=['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double']
    # VARCHAR=['varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying']
    # BOOLEAN=['bool','boolean']
    # TIMESTAMPTZ=['date','time','datetime','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone'] 
    # Create a Json Body with Specific requiremnt Mentioned accordingly and check String Values in Columns and Numbers in Rows, Check Datatypes mentioned above and Dont Mention existing same column_name in single charts rows and columns
  "charts": [
    {
      "chart_type": "Chart Type",
      "chart_title": "Chart Description",
        # Dont Repeat same column name used in row and col list
      "row": [
        # Row Should Accept Only INTEGER Datatype Columns in row list of Table Meta data
        # Get Row data List should contain, index 0 with column_name, pass "aggregate" in index 1 and index 2 with any of this sum or avg or count or min or max
        [column_name,"aggregate",sum/avg/count/min/max],[column_name,"aggregate",sum/avg/count/min/max]
      ],
      # Col should Accept Only VARCHAR, BOOLEANS AND TIMESTAMPTZ Datatype Columns in col list of table meta data 
      "col": [ 
        [column_name,column datatype,""],[column_name,column datatype,""]
      ]
    }
  ]
}"""    

def can_build_chart(meta_data, prompt,API_KEY):
    if prompt is None:
        return "YES"
    else:
        message = [{'role': 'user', 'content': f"Check whether we can build a chart based on {prompt} and {meta_data}. If we can build, respond with YES; if not, NO"}]
        try:
            API_KEY = API_KEY
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                },
                json={
                    "model": "gpt-3.5-turbo-0125",
                    "messages": message,
                    "temperature": 0.7
                }
            )
            # response.raise_for_status()
            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return {"error": "Error checking chart feasibility. Please try again later."}

def get_gpt_chart_suggestions(meta_data, prompt,API_KEY):
    if prompt is None:
        message = [{'role': 'user', 'content': f"Suggest me some charts based on the meta data provided {meta_data} in this format {format_response} only"}]
    else:
        message = [{'role': 'user', 'content': f"Build {prompt} on the meta data provided {meta_data} in this format {format_response}"}]
    
    try:
        API_KEY = API_KEY
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={
                "model": "gpt-3.5-turbo-0125",
                "messages": message,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        return {"error": "Error generating chart suggestions. Please try again later."}

def map_columns_to_datatypes(meta_data):
    column_type_map = {}
    for entry in meta_data:
        column_name = entry['column_name']
        data_type = entry['data_type']
        column_type_map[column_name] = data_type
    return column_type_map


def validate_chart_data(data, column_type_map):
    integer_datatypes = ['numeric', 'int', 'float', 'number', 'double precision', 'smallint', 'integer', 'bigint', 'decimal', 'real', 'smallserial', 'serial', 'bigserial', 'binary_float', 'binary_double']
    varchar_datatypes = ['varchar', 'bp char', 'text', 'varchar2', 'NVchar2', 'long', 'char', 'Nchar', 'character varying']
    boolean_datatypes = ['bool', 'boolean']
    timestamptz_datatypes = ['date', 'time', 'datetime', 'timestamp', 'timestamp with time zone', 'timestamp without time zone', 'timezone', 'time zone']

    valid_col_datatypes = varchar_datatypes + boolean_datatypes + timestamptz_datatypes

    corrected_charts = []

    for chart in data['charts']:
        corrected_chart = chart.copy()
        
        # Correct rows: should contain only integer types
        corrected_rows = [
            row for row in chart['row'] if column_type_map.get(row[0]) in integer_datatypes
        ]
        
        # Correct columns: should contain only valid column types
        corrected_cols = [
            col for col in chart['col'] if column_type_map.get(col[0]) in valid_col_datatypes
        ]

        corrected_chart['row'] = corrected_rows
        corrected_chart['col'] = corrected_cols

        corrected_charts.append(corrected_chart)

    return corrected_charts 

def rewrite_datatypes_for_metadata(meta_data, API_KEY):
    
    message = [{'role': 'user', 'content': f"Rewrite the JSON format by change only mentioned Datatypes  VARCHAR, INTEGER , FLOAT,BOOLEAN and DATATYPE for column {meta_data}. RETURN ONLY the JSON output based on these rules. DO NOT include any explanations or additional text."}]
    try:
        API_KEY = API_KEY
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={
                "model": "gpt-3.5-turbo-0125",
                "messages": message,
                "temperature": 0.7
            }
        )
        # response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except Exception :
        return {"error": "Error While Converting Datatypes"}

new_format = """
[
    {
        "chart_title" : "",
        "chart_type" : Chart Types should only contains Bar, Line, Pie, Donut, Area charts
        "col" : "",
        "col_datatype" : "",
        "row" : Accept Only INTEGER,FLOAT Datatype ROWS,
        "row_aggregate" : "", #Aggregate Should be SUM, AVG, MIN, MAX and COUNT,
        "row_alias": "", #Alias Name for Aggregated row if needed,
        "description":"", # Detailed Description of Chart
    },
        {
        "chart_title" : "",
        "chart_type" : Chart Types should only contains Bar, Line, Pie, Donut, Area charts
        "col" : "",
        "col_datatype" : "",
        "row" : Accept Only INTEGER,FLOAT Datatype ROWS,
        "row_aggregate" : "", #Aggregate Should be SUM, AVG, MIN, MAX and COUNT
        "row_alias": "" #Alias Name for Aggregated row if needed,
        "description":"", # Detailed Description of Chart
    },
]
"""

def chart_suggestions_on_metadata(meta_data, prompt,API_KEY):
    if prompt is None:
        # message = [{'role': 'user', 'content': f"{meta_data} \nBuild upto 10-15 Valid Chart as a list of JSON Response in below format {new_format} with columns in metadata provided"}]
        message = [
        {
            'role': 'user', 
            'content': f"""
            Metadata: {meta_data} 

            Please generate a list of 10-15 valid chart suggestions using the following rules:
            - Allowed chart types: Bar, Line, Pie, Donut, Area.
            - Each chart must have a valid title.
            - The 'col' field must contain valid column names from the metadata.
            - Only 'VARCHAR' or 'STRING' or 'DATE' or 'DATETIME' data types column names are allowed for the 'col' field.
            - Only 'INTEGER' or 'FLOAT' data types column names are allowed for the 'row' field.
            - The 'row_aggregate' field should be one of: SUM, AVG, MIN, MAX, COUNT.
            - The 'row_alias' for the aggregated row.
            RETURN ONLY the JSON output based on these rules. DO NOT include any explanations or additional text.

            {new_format}
            """
        }
        ]
    else:
        # message = [{'role': 'user', 'content': f"{meta_data} \nBuild {prompt} Chart based on JSON Response as below format {new_format} with columns in metadata provided"}]
        message = [
        {
            'role': 'user', 
            'content': f"""
            Metadata: {meta_data} 

            Please generate {prompt} valid chart suggestions using the following rules:
            - Allowed chart types: Bar, Line, Pie, Donut, Area.
            - Each chart must have a valid title.
            - The 'col' field must contain valid column names from the metadata.
            - Only 'VARCHAR' or 'STRING' or 'DATE' or 'DATETIME' data types column names are allowed for the 'col' field.
            - Only 'INTEGER' or 'FLOAT' data types column names are allowed for the 'row' field.
            - The 'row_aggregate' field should be one of: SUM, AVG, MIN, MAX, COUNT.
            - The 'row_alias' is optional and can provide an alias for the aggregated row.
            RETURN ONLY the JSON output based on these rules. DO NOT include any explanations or additional text.

            {new_format}
            """
        }
        ]
    try:
        API_KEY = API_KEY
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={
                "model": "gpt-3.5-turbo-0125",
                "messages": message,
                "temperature": 0.7
            }
        )
        response_json = response.json()
        chart_suggestions_on_metadata_status = 200
        return response_json, chart_suggestions_on_metadata_status
    except:
        chart_suggestions_on_metadata_status = 400
        chart_suggestions_on_metadata_response = "Error generating chart suggestions. Please try again later."
        return chart_suggestions_on_metadata_response, chart_suggestions_on_metadata_status

# Function to format column names
def format_column_name(column: str) -> str:
    if "." in column:
        table, col = column.split(".")
        return f"{col}({table})"
    return column

class CopilotChartSuggestionAPI(CreateAPIView):
    serializer_class = ChartCopilot
    
    def post(self, request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            usertable=UserProfile.objects.get(id=tok1['user_id'])
            userrole = UserRole.objects.get(user_id = usertable.id)
            role = Role.objects.get(role_id = userrole.role_id)
            
            if userrole.role_id == 1 and GPTAPIKey.objects.filter(added_by = usertable.id):
                gpt = GPTAPIKey.objects.get(added_by = usertable.id)
                API_KEY  =gpt.api_key
            elif not userrole.role_id == 1 :
                gpt = GPTAPIKey.objects.get(added_by = role.created_by) 
                API_KEY  =gpt.api_key
            else:
                API_KEY=''

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():   
                query_set_id = serializer.validated_data['id']
                user_prompt = serializer.validated_data['prompt']
                a = validate_api_key(API_KEY)
                
                if a.status_code ==200:
                    pass
                elif a.status_code == 401:
                    return Response({'message': a.data}, status=status.HTTP_401_UNAUTHORIZED)
                elif a.status_code == 404:
                    return Response({'message':a.data},status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':"Please try again"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                if not QuerySets.objects.filter(queryset_id=query_set_id).exists():
                    return Response({'message': "Invalid QuerySet ID"}, status=status.HTTP_404_NOT_FOUND)
                
                qs = QuerySets.objects.get(queryset_id=query_set_id)
                
                is_file =False
                if FileDetails.objects.filter(id = qs.file_id).exists() :
                    is_file = True
                    file=FileDetails.objects.get(id=qs.file_id)
                    fi_type=FileType.objects.get(id=file.file_type)
                    
                    if qs.is_custom_sql:
                        files_data =file_details(fi_type.file_type,file)
                        if files_data['status']==200:
                            engine=files_data['engine']
                            with engine.connect() as connection:
                                # Execute the custom SQL query
                                from sqlalchemy import text
                                result = connection.execute(text(qs.custom_query))
                                # Get column names
                                columns = result.keys()
                                # Fetch the result rows
                                rows = result.fetchall()
                                
                            # Prepare metadata correctly
                            meta_data = []
                            if rows:
                                for idx, column in enumerate(columns):
                                    meta_data.append({
                                        "column_name": column,
                                        # Use the index to access the value in the tuple
                                        "data_type": str(type(rows[0][idx]))  # Access using integer index, not column name
                                    })
                            meta_data = rewrite_datatypes_for_metadata(meta_data,API_KEY)
                        else:
                            return Response({"message":files_data['message']},status=files_data['status'])
                    else:                        
                        # filename = re.sub(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', '', file.display_name)
                        
                        # if fi_type.file_type=='EXCEL':
                        #     data = read_excel_file(file.source,filename,file.id)
                        # elif fi_type.file_type=='CSV':
                        #     data = read_csv_file(file.source,filename,file.id)
                        # elif fi_type.file_type=='PDF':
                        #     data = read_pdf_file(file.source,filename,file.id)
                        # elif fi_type.file_type=='TEXT':
                        #     data = read_text_file(file.source,filename,file.id)
                        # else:
                        #     return Response({'error': 'Unsupported file type/format'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        
                        # # Get the table metadata
                        # file_metadata = data["data"]["schemas"][0]["tables"]
                        file_metadata = requests.get(qs.datasource_json).json()
                        meta_data = rewrite_datatypes_for_metadata(file_metadata,API_KEY)
                        
                elif ServerDetails.objects.filter(id=qs.server_id):
                    sd = ServerDetails.objects.get(id=qs.server_id)
                    server_type = ServerType.objects.get(id=sd.server_type).server_type
                    
                    server_conn =server_connection(sd.username,sd.password,sd.database,sd.hostname,sd.port,sd.service_name,server_type.upper(),sd.database_path)
                    if server_conn['status'] != 200:
                        return Response(server_conn, status=server_conn['status'])
                    
                    engine = server_conn['engine']
                    cursor = server_conn['cursor']
                    db_type = server_type
                
                if is_file and not qs.is_custom_sql:
                    meta_data = meta_data
                    
                elif is_file and qs.is_custom_sql:
                    meta_data = meta_data
                    
                # Handle custom SQL logic
                elif not is_file and qs.is_custom_sql:
                    # Execute the custom SQL query
                    custom_sql = qs.custom_query  # Assuming there's a field `custom_sql` in QuerySets
                    try:
                        # Use the existing server connection logic
                        engine = server_conn['engine']
                        with engine.connect() as connection:
                            # Execute the custom SQL query
                            from sqlalchemy import text
                            result = connection.execute(text(custom_sql))
                            # Get column names
                            columns = result.keys()

                            # Fetch the result rows
                            rows = result.fetchall()
                        # Prepare metadata correctly
                        meta_data_list = []
                        if rows:
                            for idx, column in enumerate(columns):
                                meta_data_list.append({
                                    "column_name": column,
                                    # Use the index to access the value in the tuple
                                    "data_type": str(type(rows[0][idx]))  # Access using integer index, not column name
                                })
                        else:
                            # Handle the case where there are no rows
                            for column in columns:
                                meta_data_list.append({
                                    "column_name": column,
                                    "data_type": "No data"
                                })
                        meta_data_after_validaing_datatypes = rewrite_datatypes_for_metadata(meta_data_list,API_KEY)
                        meta_data = meta_data_after_validaing_datatypes
                    except Exception as e:
                        return Response({"message": f"Error executing custom SQL: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                elif not is_file and not qs.is_custom_sql :
                    # # Create a list to store the results in schema.table_name format
                    # tables_list = qs.table_names
                    # tables_list = ast.literal_eval(tables_list)
                    # tables = []

                    # # Iterate through the list
                    # for entry in tables_list:
                    #     if len(entry) == 2:
                    #         schema, table = entry
                    #     elif len(entry) == 3:
                    #         schema, table, _ = entry  # Ignore the alias part
                    #     else:
                    #         continue  # Skip entries that don't match the expected structure
                    #     tables.append(f"{schema}.{table}")
                    # result = get_table_meta_data(engine, cursor, tables, db_type)
                    # if isinstance(result, dict) and 'data' in result:
                    #     result_data_str = json.dumps(result['data'])
                    #     op = ast.literal_eval(result_data_str)
                    # else:
                    #     return Response({"message": "Error fetching table metadata."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    meta_data = requests.get(qs.datasource_json).json()
                else:
                    return Response({'message':"Error Generating Meta Data"},status=status.HTTP_406_NOT_ACCEPTABLE)
                chart_suggestions_response,chart_suggestions_status  =chart_suggestions_on_metadata(meta_data,user_prompt,API_KEY)
                
                if chart_suggestions_status == 200:
                    output = chart_suggestions_response['choices'][0]['message']['content']
                    data = json.loads(output)
                    output_data = {
                        "data": []
                    }

                    chart_type_mapping = {
                        "Bar": "Bar Chart",
                        "Pie": "Pie Chart",
                        "Line": "Line Chart",
                        "Donut": "Donut Chart",
                        "Area": "Area Chart",
                        "Table": "Tables"
                    }
                    
                    # Chart type to chart ID mapping
                    chart_id_mapping = {
                        "Area": 17,
                        "Pie": 24,
                        "Line": 13,
                        "Bar": 6,
                        "Table": 1,
                        "Donut": 10
                    }

                    for chart in data:
                        chart_type_lower = chart["chart_type"].lower().replace(" chart", "")  # Normalize the chart type to lowercase
                        formatted_chart = {
                            "chart_title": chart["chart_title"],
                            "chart_type": chart_type_mapping.get(chart_type_lower, chart["chart_type"]),
                            "database_id": qs.server_id,
                            "queryset_id": qs.queryset_id,
                            "col": [
                                [
                                    format_column_name(chart["col"]),  # Format column name,
                                    chart["col_datatype"].upper(),
                                    "",
                                    ""
                                ]
                            ],
                            "row": [
                                [
                                    format_column_name(chart["row"]),  # Format column name
                                    "aggregate",
                                    chart["row_aggregate"].lower(),
                                    chart["row_alias"] if "row_alias" in chart else ""
                                ]
                            ],
                            "filter_id": [],
                            "columns": [
                                {
                                    "column": format_column_name(chart["col"]),  # Format column name
                                    "data_type": chart["col_datatype"].upper()
                                }
                            ],
                            "rows": [
                                {
                                    "column": format_column_name(chart["row"]),  # Format column name
                                    "type": chart["row_aggregate"].lower()
                                }
                            ],
                            "datasource_quertsetid": "",
                            "sheetfilter_querysets_id": "",
                            "chart_id": chart_id_mapping.get(chart["chart_type"], 0),  # Assign chart_id based on the type
                            "description":chart["description"] if "description" in chart else ""
                        }
                        
                        output_data["data"].append(formatted_chart)
                    # Resulting output
                    return Response(output_data)
                else :
                    return Response({'message':chart_suggestions_response})
            else:
                return Response({'message':"Serialzier Error"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])