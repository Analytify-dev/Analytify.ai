from simple_salesforce import Salesforce
from quickbooks import salesforce,serializers,views as qb_views
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from quickbooks import models as qb_models, salesforce
import datetime
from pytz import utc
from rest_framework.generics import CreateAPIView
from dashboard import views,columns_extract,Connections
from project import settings


domain = settings.SALESFORCE_DOMAIN

def salesforce_token(sf_id,tok1):
    qb_id_1=columns_extract.parent_child_ids(sf_id,parameter="salesforce")
    tokst=salesforce.sf_status_check(tok1['user_id'],qb_id_1)
    if tokst['status']==200:
        pass
    else:
        return Response({'message':tokst['message']},status=tokst['status'])
    tokac=qb_models.TokenStoring.objects.get(user=tok1['user_id'],salesuserid=qb_id_1)
    if tokac.expiry_date > datetime.datetime.now(utc):
        data = {
            "data":tokac,
            "status":200
        }
        return data
    else:
        rftk=salesforce.token_access_refresh(sf_id,tok1['user_id'])
        if rftk['status']==200:
            tokac = qb_models.TokenStoring.objects.get(user=tok1['user_id'],salesuserid=qb_id_1)
            data = {
                "data":tokac,
                "status":200
            }
        else:
            data={
                "status":rftk['status'],
                "data":rftk
            }
            # return Response(st_dt,status=st_dt['status'])
        return data
                

def table_columns(sf_id,tok1,display_name,queryset_name,search):
    token_status=salesforce_token(sf_id,tok1)
    if token_status['status']==200:
        tokac=token_status['data']
    else:
        return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])
    url = f"{domain}/services/data/v43.0/sobjects"
    headers = {
        'Authorization': f'Bearer {str(tokac.accesstoken)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code==200:
        data = response.json()
        if search=='' or search==None or search=="":
            tables_list=[tb['label'] for tb in data['sobjects']]
        else:
            objects = data['sobjects']
            ac_objects = [obj for obj in objects if str(search) in str(obj['name']).lower()]
            tables_list=[obj['name'] for obj in ac_objects]

        fn_dt=[]
        table_qb=[]
        for tabl in tables_list:
            describe_endpoint = f'{domain}/services/data/v53.0/sobjects/{tabl}/describe'
            headers = {
                'Authorization': f'Bearer {str(tokac.accesstoken)}',
                'Content-Type': 'application/json'
            }
            response = requests.get(describe_endpoint, headers=headers)
            if response.status_code==200:
                fields = response.json().get('fields', [])
                column_info = [
                    {"column": field['name'], "datatype": field['type']}
                    for field in fields
                ]
                table_qb.append({"schema":display_name,"table":tabl,"columns":column_info})
            else:
                pass
        schemaqb = [{"schema":display_name,"tables":table_qb}]  ##{"schema":quicboooks_tb.display_name,"tables":[]},
        
        # table_names = []
        # for schema in schemaqb:
        #     for table in schema['tables']:
        #         table_names.append(table['table'])

        return Response(
            {
                "message": "Successfully Connected to salesforce",
                "queryset_name":queryset_name,
                "data": {"schemas":schemaqb},
                'display_name': display_name,
            }, status=status.HTTP_200_OK)
    else:
        return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=response.status_code)


def salesforce_query_data(server_id,tok1,tabl_name):
    token_status=salesforce_token(server_id,tok1)
    if token_status['status']==200:
        tokac=token_status['data']
    else:
        return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])
    describe_endpoint = f'{domain}/services/data/v53.0/sobjects/{tabl_name}/describe'
    headers = {
        'Authorization': f'Bearer {str(tokac.accesstoken)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(describe_endpoint, headers=headers)
    if response.status_code==200:
        fields = response.json().get('fields', [])
        column_names = [field['name'] for field in fields]
        columns_string = ', '.join(column_names)
        query_fn = f"SELECT {columns_string} FROM {tabl_name}"
        api_endpoint = f'{domain}/services/data/v53.0/query/?q={query_fn}'
        headers = {
            'Authorization': f'Bearer {tokac.accesstoken}',
            'Content-Type': 'application/json' 
        }
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code==200:
            data = response.json()
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])
    else:
        return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])        
                

class query_data(CreateAPIView):
    serializer_class=serializers.query_serializer

    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                table_name = serializer.validated_data['table_name']
                database_id = serializer.validated_data['database_id']
                pr_id=views.parent_ids.objects.get(id=database_id)
                if pr_id.parameter=='salesforce':
                    data=salesforce_query_data(database_id,tok1,table_name)
                elif pr_id.parameter=='quickbooks':
                    data=qb_views.quickbooks_query_data(database_id,tok1,table_name)
                return data
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])



@api_view(['GET'])
def to_fetch_all_tables_details(request,sf_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            tokst=salesforce_token(sf_id,tok1)
            if tokst['status']==200:
                quicboooks_tb=tokst['data']
            else:
                return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=tokst['status'])
            queryset_name=None
            search=None
            qtable_qb=table_columns(sf_id,tok1,quicboooks_tb.display_name,queryset_name,search)
            return qtable_qb
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['GET'])
def get_salesforce_user_info(request,sf_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            token_status=salesforce_token(sf_id,tok1)
            if token_status['status']==200:
                tokac=token_status['data']
            else:
                return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])
            url = f"{domain}/services/oauth2/userinfo"
            headers = {
                'Authorization': f'Bearer {str(tokac.accesstoken)}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers)
            if response.status_code==200:
                data = response.json()
                return Response({"data":data},status=status.HTTP_200_OK)
            else:
                return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=response.status_code)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['GET'])
def accounts_data(request,sf_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            token_status=salesforce_token(sf_id,tok1)
            if token_status['status']==200:
                tokac=token_status['data']
            else:
                return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=token_status['status'])
            describe_endpoint = f'{domain}/services/data/v53.0/sobjects/Account/describe'
            headers = {
                'Authorization': f'Bearer {tokac.accesstoken}',
                'Content-Type': 'application/json'
            }
            describe_response = requests.get(describe_endpoint, headers=headers)
            if describe_response.status_code != 200:
                return Response({'message': 'Failed to describe object'}, status=status.HTTP_400_BAD_REQUEST)
            fields = describe_response.json().get('fields', [])
            field_names = [field['name'] for field in fields]
            query1 = ', '.join(field_names)
            query = f'SELECT {query1} FROM Account'

            api_endpoint = f'{domain}/services/data/v53.0/query/?q={query}'
            headers = {
                'Authorization': f'Bearer {tokac.accesstoken}',
                'Content-Type': 'application/json' 
            }
            response = requests.get(api_endpoint, headers=headers)
            if response.status_code==200:
                data = response.json()
                return Response({"data":data},status=status.HTTP_200_OK)
            else:
                return Response({'message':'session expired, login to salesforce again',"SalesforceConnected":False},status=response.status_code)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
