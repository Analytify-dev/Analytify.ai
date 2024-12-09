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
    
    def get(self,request,token):
        tok1 = test_token(token)
        if tok1['status']==200:
            data = GPTAPIKey.objects.filter(added_by = tok1['user_id']).values()
            return Response({'message':data})
        else:
            return Response(tok1,status=tok1['status'])


def validate_api_key(KEY):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{'role': 'user', 'content': "Say this is a test"}]
            # 'max_tokens':5
        }
    )

    if response.status_code == 200:
        return Response({'message': True}, status=status.HTTP_200_OK)
    elif response.status_code == 404:
        res = {
            'error': {
                'message': 'The model `gpt-3.5-turbo` does not exist or you do not have access to it.',
                'type': 'invalid_request_error',
                'param': None,
                'code': 'model_not_found'
            }
        }
        return Response({'message': res['error']['message']}, status=status.HTTP_404_NOT_FOUND)
    elif response.status_code == 401:
        return Response({'message': f"Incorrect API key provided: '{KEY}'. \n\n You can find your API key at https://platform.openai.com/account/api-keys."}, status=status.HTTP_401_UNAUTHORIZED)
    elif response.status_code == 429:
        res = {
            'error': {
                'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.',
                'type': 'insufficient_quota',
                'param': None,
                'code': 'insufficient_quota'
            }
        }
        return Response({'message': res['error']['message']}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Handle unexpected status codes
    return Response({'message': 'An unexpected error occurred.'}, status=response.status_code)


class CopilotChartSuggestionAPI(CreateAPIView):
    serializer_class = ChartCopilot
    
    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])
        
        # Fetch User, Role, and API key
        usertable = UserProfile.objects.get(id=tok1['user_id'])
        userrole = UserRole.objects.get(user_id=usertable.id)
        role = Role.objects.get(role_id=userrole.role_id)
        
        if userrole.role_id == 1 and GPTAPIKey.objects.filter(added_by=usertable.id).exists():
            gpt = GPTAPIKey.objects.get(added_by=usertable.id)
            API_KEY = gpt.api_key
        elif userrole.role_id != 1 and GPTAPIKey.objects.filter(added_by=role.created_by).exists():
            gpt = GPTAPIKey.objects.get(added_by=role.created_by)
            API_KEY = gpt.api_key
        else:
            API_KEY = ''
        
        # Validate serializer
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'message': "Serializer Error"}, status=status.HTTP_400_BAD_REQUEST)

        query_set_id = serializer.validated_data['id']
        user_prompt = serializer.validated_data['prompt']
        
        # Validate API key
        api_validation = validate_api_key(API_KEY)
        if api_validation.status_code != 200:
            return Response({'message': api_validation.data}, status=api_validation.status_code)

        # Check if the queryset ID exists
        if not QuerySets.objects.filter(queryset_id=query_set_id).exists():
            return Response({'message': "Invalid QuerySet ID"}, status=status.HTTP_404_NOT_FOUND)
        
        qs = QuerySets.objects.get(queryset_id=query_set_id)

        if not qs.file_id in ("",None," ") and qs.is_custom_sql == True:
            file = FileDetails.objects.get(id=qs.file_id)
            fi_type = FileType.objects.get(id=file.file_type)
            if qs.is_custom_sql:
                files_data = file_details(fi_type.file_type, file)
                if files_data['status'] != 200:
                    return Response({"message": files_data['message']}, status=files_data['status'])
                
                engine = files_data['engine']
                with engine.connect() as connection:
                    result = connection.execute(text(qs.custom_query))
                    columns = result.keys()
                    rows = result.fetchall()
                
                meta_data = [
                    {"column_name": column, "data_type": str(type(rows[0][idx]))}
                    for idx, column in enumerate(columns)
                ] if rows else [
                    {"column_name": column, "data_type": "No data"}
                    for column in columns
                ]
                meta_data = rewrite_datatypes_for_metadata(meta_data, API_KEY)
            else:
                # Load data based on file type
                filename = re.sub(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', '', file.display_name)
                data_loaders = {
                    'EXCEL': read_excel_file,
                    'CSV': read_csv_file,
                    'PDF': read_pdf_file,
                    'TEXT': read_text_file
                }
                data_loader = data_loaders.get(fi_type.file_type)
                if not data_loader:
                    return Response({'error': 'Unsupported file type/format'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                data = data_loader(file.source, filename, file.id)
                meta_data = rewrite_datatypes_for_metadata(data["data"]["schemas"][0]["tables"], API_KEY)
        
        elif not qs.server_id in ("",None," ") and qs.is_custom_sql == True:
            sd = ServerDetails.objects.get(id=qs.server_id)
            server_type = ServerType.objects.get(id=sd.server_type).server_type.upper()
            server_conn = server_connection(sd.username, sd.password, sd.database, sd.hostname, sd.port, sd.service_name, server_type, sd.database_path)
            if server_conn['status'] != 200:
                return Response(server_conn, status=server_conn['status'])
            
            engine = server_conn['engine']
            cursor = server_conn['cursor']
            db_type = server_type

            if qs.is_custom_sql:
                try:
                    with engine.connect() as connection:
                        result = connection.execute(text(qs.custom_query))
                        columns = result.keys()
                        rows = result.fetchall()
                    
                    meta_data = [
                        {"column_name": column, "data_type": str(type(rows[0][idx]))}
                        for idx, column in enumerate(columns)
                    ] if rows else [
                        {"column_name": column, "data_type": "No data"}
                        for column in columns
                    ]
                    meta_data = rewrite_datatypes_for_metadata(meta_data, API_KEY)
                except Exception as e:
                    return Response({"message": f"Error executing custom SQL: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                tables_list = ast.literal_eval(qs.table_names)
                tables = [f"{schema}.{table}" for entry in tables_list if (len(entry) == 2 or len(entry) == 3) and (schema := entry[0]) and (table := entry[1])]
                result = get_table_meta_data(engine, cursor, tables, db_type)
                
                if isinstance(result, dict) and 'data' in result:
                    meta_data = ast.literal_eval(json.dumps(result['data']))
                else:
                    return Response({"message": "Error fetching table metadata."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # if  not qs.is_custom_sql and qs. 
            request_data = requests.get(qs.datasource_json).json()

            meta_data ,code = rewrite_datatypes_for_metadata(request_data,API_KEY)
            if code == 200 :
                meta_data = meta_data
            else:
                meta_data = request_data.json()

        chart_suggestions_response, chart_suggestions_status = chart_suggestions_on_metadata(meta_data, user_prompt, API_KEY)
        if chart_suggestions_status == 200:
            output = chart_suggestions_response['choices'][0]['message']['content']

            if output.startswith("```json"):
                output = output[7:-3].strip()

            data = json.loads(output)
            output_data = {"data": []}
            
            chart_type_mapping = {
                "Bar": "Bar Chart",
                "Pie": "Pie Chart",
                "Line": "Line Chart",
                "Donut": "Donut Chart",
                "Area": "Area Chart",
                "Table": "Tables"
            }
            
            chart_id_mapping = {
                "Area": 17,
                "Pie": 24,
                "Line": 13,
                "Bar": 6,
                "Table": 1,
                "Donut": 10
            }
            
            for chart in data:
                chart_type_lower = chart["chart_type"].lower().replace(" chart", "")
                formatted_chart = {
                    "chart_title": chart["chart_title"],
                    "chart_type": chart_type_mapping.get(chart_type_lower, chart["chart_type"]),
                    "database_id": qs.server_id,
                    "queryset_id": qs.queryset_id,
                    "col": [[format_column_name(chart["col"]), chart["col_datatype"].upper(), "", ""]],
                    "row": [[format_column_name(chart["row"]), "aggregate", chart["row_aggregate"].lower(), chart.get("row_alias", "")]],
                    "filter_id": [],
                    "columns": [{"column": format_column_name(chart["col"]), "type": chart["col_datatype"].upper()}],
                    "rows": [{"column": format_column_name(chart["row"]), "type": chart["row_aggregate"].lower()}],
                    "datasource_quertsetid": "",
                    "sheetfilter_querysets_id": "",
                    "chart_id": chart_id_mapping.get(chart["chart_type"], 0),
                    "description": chart["description"]
                }
                output_data["data"].append(formatted_chart)
            
            return Response(output_data)
        
        return Response({'message': chart_suggestions_response})
    
def chart_suggestions_on_metadata(meta_data, prompt, API_KEY):
    # Define the message based on whether a prompt is provided
    if prompt is None:
        message = [
                {
                    'role': 'user',
                    'content': f"""
                        Metadata: {meta_data}

                        You MUST generate a list of valid chart suggestions based on the following STRICT rules:
                        - Allowed chart types: Bar, Line, Pie, Donut, Area.
                        - Each chart MUST have a valid title.
                        - The 'col' field MUST contain valid column names from the metadata with categorical data types (TEXT, STRING,BOOLEAN, DATE, DATETIME).
                        - The 'row' field MUST contain valid column names with 'INTEGER' or 'FLOAT' data types only.
                        - For Pie and Donut charts, use 'count' for aggregation on categorical fields.
                        - The 'row_aggregate' field MUST be one of: SUM, AVG, MIN, MAX, COUNT.
                        - The 'row_alias' is OPTIONAL and can provide an alias for the aggregated row.
                        - Ensure that the data types STRICTLY align with the selected chart type (e.g., avoid averaging BOOLEAN columns).

                        RETURN ONLY the JSON output based on these rules. DO NOT include any explanations or additional text.

                        {new_format}
                    """
                }
        ]
    else:
        message = [
                    {
                        'role': 'user',
                        'content': f"""
                        Metadata: {meta_data}

                        You MUST generate {prompt} valid chart suggestions using the following STRICT rules:
                        - Allowed chart types: Bar, Line, Pie, Donut, Area.
                        - Each chart MUST have a valid title.
                        - The 'col' field MUST contain valid column names from the metadata with categorical data types (TEXT, STRING,BOOLEAN, DATE, DATETIME).
                        - The 'row' field MUST contain valid column names with 'INTEGER' or 'FLOAT' data types only.
                        - For Pie and Donut charts, use 'count' for aggregation on categorical fields.
                        - The 'row_aggregate' field MUST be one of: SUM, AVG, MIN, MAX, COUNT.
                        - The 'row_alias' is OPTIONAL and can provide an alias for the aggregated row.
                        - Ensure the data types STRICTLY align with the selected chart type (e.g., avoid averaging BOOLEAN columns).

                        RETURN ONLY the JSON output based on these rules. DO NOT include any explanations or additional text.

                        {new_format}
                        """
                    }
                ]
    
    try:
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
    except Exception as e:
        print(f"Error: {e}")
        chart_suggestions_on_metadata_status = 400
        chart_suggestions_on_metadata_response = "Error generating chart suggestions. Please try again later."
        return chart_suggestions_on_metadata_response, chart_suggestions_on_metadata_status



    

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


def format_column_name(column: str) -> str:
    if "." in column:
        table, col = column.split(".")
        return f"{col}({table})"
    return column


def rewrite_datatypes_for_metadata(meta_data, API_KEY):
    # Prepare the request message to modify only specified datatypes
    message = [
        {
            'role': 'user',
            'content': (
                f"Rewrite the JSON format for the provided metadata. Change the datatype "
                f"only for the following types: VARCHAR, INTEGER, FLOAT, BOOLEAN, and DATE. "
                f"Make these updates for the metadata: {meta_data}. Return only the JSON output without any explanation."
            )
        }
    ]
    
    # Make the API request
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

    # Check if the request was successful
    response.raise_for_status()

    # Parse the JSON response
    response_json = response.json()

    # Extract the modified content
    content = response_json.get('choices', [])[0].get('message', {}).get('content', None)
    # Remove non-JSON text if any
    if content:
        start_index = content.find("[")
        end_index = content.rfind("]") + 1
        content = content[start_index:end_index]
    return content , 200

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