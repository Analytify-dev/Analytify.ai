import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
from dashboard import views,models as dshb_models,Connections,columns_extract,clickhouse
from quickbooks import models,serializers,endpoints_data
import datetime
from io import BytesIO
from pytz import utc
from requests.auth import HTTPBasicAuth
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
from django.core.mail import send_mail
from urllib.parse import urlparse, parse_qs
from requests_oauthlib import OAuth2Session
import json,io
from sqlalchemy import text
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from base64 import b64encode


# apicn_urls = ['company/companies','company/configurations','service/tickets']

apicn_urls = ['company/companies','company/configurations','service/tickets','company/contacts','sales/stages',
              'sales/opportunities','sales/probabilities','system/departments','procurement/catalog','company/countries',
              'marketing/groups/info']

# urls = ['companies','configurations','tickets']

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now(utc)+datetime.timedelta(minutes=60)

# swagger_url = "https://api-na.myconnectwise.net/v4_6_release/apis/3.0/swagger/docs/v1"
# swagger_url = https://api.tierpoint.com/api/v1/connectwise/swagger-ui/index.html?utm_source=chatgpt.com

def connection_error_messages(company_id,site_url,public_key,private_key,client_id,display_name,user_id,conne_id):
    print(conne_id)
    if display_name=='' or display_name==None or display_name ==' ' or display_name=="":
        return Response({'message':"Display name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif company_id=='' or company_id==None or company_id ==' ' or company_id == "":
        return Response({'message':"company_id Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif site_url=='' or site_url==None or site_url ==' ' or site_url=="":
        return Response({'message':"site_url Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif public_key=='' or public_key==None or public_key ==' 'or public_key=="":
        return Response({'message':"Public key be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif private_key=='' or private_key==None or private_key ==' 'or private_key=="":
        return Response({'message':"Private key be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif models.connectwise.objects.filter(user_id=user_id,display_name=display_name).exclude(id=conne_id).exists():
        return Response({'message':"Display Name Already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif client_id==None or client_id=='' or client_id=="" or client_id==' ': 
        return Response({'message':"client_id Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        if conne_id is not None:
            if models.connectwise.objects.filter(user_id=user_id,id=conne_id).exists():
                return 200
            else:
                return Response({'message':"Connectwise_id not exists"},status=status.HTTP_404_NOT_FOUND)
        else:
            return 200
        
    
@transaction.atomic
def connectwise_main(serializer,parameter,tok1):
    company_id = serializer.validated_data['company_id']
    site_url = serializer.validated_data['site_url']
    public_key = serializer.validated_data['public_key']
    private_key1 = serializer.validated_data['private_key']
    client_id = serializer.validated_data['client_id']
    display_name = serializer.validated_data['display_name']
    connectwise_id = serializer.validated_data['hierarchy_id']

    private_key=views.encode_string(private_key1)

    if parameter=='UPDATE':
        parent_ids=dshb_models.parent_ids.objects.get(id=connectwise_id,parameter='connectwise')
        connect_id=parent_ids.table_id
    else:
        connect_id=connectwise_id

    error_msg=connection_error_messages(company_id,site_url,public_key,private_key1,client_id,display_name,tok1['user_id'],connect_id)
    if error_msg==200:
        pass
    else:
        return error_msg

    endpoint = "/v4_6_release/apis/3.0/company/companies"
    auth_token = b64encode(
        f"{company_id}+{public_key}:{private_key1}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_token}",
        "clientID": client_id,
        "Content-Type": "application/json"
    }
    response = requests.get(f"{site_url}{endpoint}", headers=headers)
    if response.status_code == 200:
        # data1 = response.json()
        database=display_name
        click = clickhouse.Clickhouse()
        if parameter=='SAVE':
            cwtb=models.connectwise.objects.create(user_id=tok1['user_id'],company_id=company_id,site_url=site_url,public_key=public_key,private_key=private_key,client_id=client_id,display_name=display_name)
            parent_ids=dshb_models.parent_ids.objects.create(table_id=cwtb.id,parameter='connectwise')
            message="Successfully connected"
        elif parameter=='UPDATE':
            if connectwise_id==None or connectwise_id=='' or connectwise_id=="":
                return Response({'message':'Empty hierarchy_id is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            models.connectwise.objects.filter(user_id=tok1['user_id'],id=connect_id).update(company_id=company_id,site_url=site_url,public_key=public_key,private_key=private_key,client_id=client_id,display_name=display_name,updated_at=updated_at)
            click.cursor.execute(text(f'Drop Database if Exists \"{database}\"'))
            parent_ids=dshb_models.parent_ids.objects.get(id=connectwise_id,parameter='connectwise')
            message="Updated Successfully"
        else:
            pass

        click.client.query(f'Create Database if Not Exists \"{database}\"')
        result = click.json_to_table(apicn_urls,tok1,parent_ids.id,database,'connectwise')
        if result['status']==200:
            data = {
                "message":message,
                "hierarchy_id":parent_ids.id,
                "connected":True
            }
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(result['message'],status=result['status'])
    else:
        return Response({"connected":False,"message":"Invalid credentials"},status=response.status_code)


class connecwise_integrate(CreateAPIView):
    serializer_class=serializers.connectwise_serializer

    @csrf_exempt
    @transaction.atomic
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                parameter='SAVE'
                result=connectwise_main(serializer,parameter,tok1)
                return result
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
        
    
    @csrf_exempt
    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                parameter='UPDATE'
                result=connectwise_main(serializer,parameter,tok1)
                return result
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])


def connectwise_data(urlendpoint,cn_id):
    pr_id=dshb_models.parent_ids.objects.get(id=cn_id,parameter='connectwise')
    cn_data=models.connectwise.objects.get(id=pr_id.table_id)
    endpoint = "/v4_6_release/apis/3.0/{}".format(urlendpoint)
    password1234=views.decode_string(cn_data.private_key)
    auth_token = b64encode(
        f"{cn_data.company_id}+{cn_data.public_key}:{password1234}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_token}",
        "clientID": cn_data.client_id,
        "Content-Type": "application/json"
    }
    response = requests.get(f"{cn_data.site_url}{endpoint}", headers=headers)
    if response.status_code == 200:
        data1 = response.json()
        d1 = {
            "data":data1,
            "status":200
        }
    else:
        d1 = {
            "data":None,
            "status":400
        }
    return d1

