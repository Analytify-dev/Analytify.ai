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
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from base64 import b64encode



created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now(utc)+datetime.timedelta(minutes=60)

apicn_urls = [
            'users', 'Client', 'Webhook', 'UserRoles', 'AssetTypeInfo', 'Agent', 
            'Status', 'ToDoGroup', 'Timesheet', 'Tax', 'Tags', 'Tabs', 'PurchaseOrder', 
            'SlackDetails', 'Site', 'Service', 'Team', 'Schedule', 'SalesMailbox', 
            'TicketType', 'Product', 'ReleasePipeline', 'ProductComponent', 'Release', 
            'Quotation', 'Projects', 'Priority', 'Organisation', 
            'OrderLine', 'SalesOrder', 'Opportunities', 'OnlineStatus', 'Roles', 'Application', 
            'Features', 'EmailTemplate', 'Mailbox', 'Lookup', 'Chat', 
            'LicenseInfo', 'Languages', 'JiraDetails', 'Item', 'Invoice', 'Instance', 
            'Holiday', 'AssetGroup', 'Feedback', 'ToDO', 'Tickets', 'Event', 
            'Asset', 'DashboardLinks', 'Currency', 'Supplier', 'Category', 
            'CallLog', 'CAB', 'BudgetType', 'TicketRules', 'Attachment', 'CRMNote', 
            'Report', 'AISuggestion', 'Address', 'Actions'
        ]  

# Fail = ['QuickBookDetails', 'Outgoing', 'MO', 'MailCampaign', 'EcommerceOrder', 'Audit','configurationitems','services','tickets',]
# apicn_urls = ['tickets', 'users', 'Client']  #'configurationitems','services',


def connection_error_messages(site_url,client_id,client_secret,display_name,user_id,conne_id):
    if display_name=='' or display_name==None or display_name ==' ' or display_name=="":
        return Response({'message':"Display name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif client_secret=='' or client_secret==None or client_secret ==' ' or client_secret == "":
        return Response({'message':"company_id Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif site_url=='' or site_url==None or site_url ==' ' or site_url=="":
        return Response({'message':"site_url Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif models.HaloPs.objects.filter(user_id=user_id,display_name=display_name).exclude(id=conne_id).exists():
        return Response({'message':"Display Name Already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif client_id==None or client_id=='' or client_id=="" or client_id==' ': 
        return Response({'message':"client_id Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        if conne_id is not None:
            if models.HaloPs.objects.filter(user_id=user_id,id=conne_id).exists():
                return 200
            else:
                return Response({'message':"HaloPs_id not exists"},status=status.HTTP_404_NOT_FOUND)
        else:
            return 200
        
@transaction.atomic
def halops_main(serializer,parameter,tok1):
    site_url = serializer.validated_data['site_url']
    client_id = serializer.validated_data['client_id']
    client_secret1 = serializer.validated_data['client_secret']
    display_name = serializer.validated_data['display_name']
    halops_id = serializer.validated_data['hierarchy_id']

    client_secret=views.encode_string(client_secret1)

    if parameter=='UPDATE':
        parent_ids=dshb_models.parent_ids.objects.get(id=halops_id,parameter='halops')
        halo_id=parent_ids.table_id
    else:
        halo_id=halops_id
    error_msg=connection_error_messages(site_url,client_id,client_secret1,display_name,tok1['user_id'],halo_id)
    if error_msg==200:
        pass
    else:
        return error_msg
    
    url="{}/auth/token".format(site_url)
    ## for client_credentials mechanism there is no refresh token generation.
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret1,
        'scope':'all'
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        database=display_name
        click = clickhouse.Clickhouse()
        if parameter=='SAVE':
            hatb=models.HaloPs.objects.create(user_id=tok1['user_id'],client_id=client_id,client_secret=client_secret,site_url=site_url,access_token=data['access_token'],display_name=display_name,expiry_date=expired_at)
            parent_ids=dshb_models.parent_ids.objects.create(table_id=hatb.id,parameter='halops')
            message="Successfully connected"
        elif parameter=='UPDATE':
            if halops_id==None or halops_id=='' or halops_id=="":
                return Response({'message':'Empty hierarchy_id is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            models.HaloPs.objects.filter(user_id=tok1['user_id'],id=halo_id).update(client_id=client_id,client_secret=client_secret,site_url=site_url,access_token=data['access_token'],display_name=display_name,updated_at=updated_at,expiry_date=expired_at)
            click.cursor.execute(text(f'Drop Database if Exists \"{database}\"'))
            parent_ids=dshb_models.parent_ids.objects.get(id=halops_id,parameter='halops')
            message="Updated Successfully"

        click.client.query(f'Create Database if Not Exists \"{database}\"')
        result = click.json_to_table(apicn_urls,tok1,parent_ids.id,database,'halops')
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

        
    
class halops_integrate(CreateAPIView):
    serializer_class=serializers.halops_serializer

    @csrf_exempt
    @transaction.atomic
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                parameter='SAVE'
                result=halops_main(serializer,parameter,tok1)
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
                result=halops_main(serializer,parameter,tok1)
                return result
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
        

def halops_refresh_token(cn_id):
    pr_id=dshb_models.parent_ids.objects.get(id=cn_id,parameter='halops')
    cn_data=models.HaloPs.objects.get(id=pr_id.table_id)
    cl_client=views.decode_string(cn_data.client_secret)
    url="{}/auth/token".format(cn_data.site_url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'client_credentials',
        'client_id': cn_data.client_id,
        'client_secret': cl_client,
        'scope':'all'
    }
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    models.HaloPs.objects.filter(id=pr_id.table_id).update(access_token=data['access_token'],expiry_date=expired_at)


def main_data(cn_data,urlendpoint):
    headers = {
        "Authorization": f"Bearer {cn_data.access_token}",
        "Content-Type": "application/json"
    }
    api_endpoint="{}/api/{}".format(cn_data.site_url,urlendpoint)
    response = requests.get(api_endpoint, headers=headers)
    if response.status_code==200:
        data1=response.json()
        return response.status_code,data1
    else:
        data1=None
        return response.status_code,data1


def halops_data(urlendpoint,cn_id):
    pr_id=dshb_models.parent_ids.objects.get(id=cn_id,parameter='halops')
    cn_data=models.HaloPs.objects.get(id=pr_id.table_id)
    response,data=main_data(cn_data,urlendpoint)
    if response == 200:
        data1 = data
        d1 = {
            "data":data1,
            "status":200
        }
    elif response == 401:
        halops_refresh_token(cn_id)
        cn_data1=models.HaloPs.objects.get(id=pr_id.table_id)
        response,data11=main_data(cn_data1,urlendpoint)
        if response==200:
            data1=data11
            d1 = {
                "data":data1,
                "status":200
            }
        else:
            d1 = {
                "data":None,
                "status":400
            }
    else:
        d1 = {
            "data":None,
            "status":400
        }
    return d1