import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
import pkce,base64,hashlib
from dashboard import views,columns_extract
from quickbooks import models,serializers,endpoints_data,views as qb_views
from dashboard import models as dshb_models,clickhouse
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
import urllib.parse
import requests
from sqlalchemy import text
from django.shortcuts import redirect


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now(utc)+datetime.timedelta(minutes=60)


api_urls = ['products','orders','customers','price_rules','shipping_zones','script_tags']

# urls = ['inventory_levels','fulfillments',,'shopify_payments/balance']


def shopify_error(api_token,shop_name,display_name,user_id,id):
    if api_token=='' or api_token==None or api_token ==' ' or api_token=="":
        return Response({'message':"api token Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif shop_name=='' or shop_name==None or shop_name ==' ' or shop_name=="":
        return Response({'message':"shop name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif display_name=='' or display_name==None or display_name ==' ' or shop_name=="":
        return Response({'message':"display name Can't be Empty"},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif models.Shopify.objects.filter(user_id=user_id,display_name=display_name).exclude(id=id).exists():
        return Response({'message':"Display Name Already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return 200


def shopift_main(serializer,tok1,parameter):
    api_token1 = serializer.validated_data['api_token']
    shop_name = serializer.validated_data['shop_name']
    display_name = serializer.validated_data['display_name']
    shopify_id = serializer.validated_data['hierarchy_id']
    api_version = "2024-01"

    api_token=views.encode_string(api_token1)

    if parameter=='UPDATE':
        parent_ids=dshb_models.parent_ids.objects.get(id=shopify_id,parameter='shopify')
        shop_id=parent_ids.table_id
    else:
        shop_id=shopify_id

    sh_error=shopify_error(api_token,shop_name,display_name,tok1['user_id'],shop_id)
    if not sh_error==200:
        return sh_error
    headers = {
        "X-Shopify-Access-Token": api_token1,
        "Content-Type": "application/json"
    }
    url = f"https://{str(shop_name)}/admin/api/{str(api_version)}/shop.json"
    try:
        response = requests.get(url, headers=headers)
        d1 = response.json()
    except:
        return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
    click = clickhouse.Clickhouse()
    database=display_name
    if response.status_code==200:
        if parameter=='SAVE':
            shoptb=models.Shopify.objects.create(
                api_token=api_token,
                shop_name=shop_name,
                user_id=tok1['user_id'],
                api_version=api_version,
                display_name=display_name
            )
            shoptb.save()
            parent_ids=dshb_models.parent_ids.objects.create(table_id=shoptb.id,parameter='shopify')
            message = 'connected successfully'
        elif parameter=='UPDATE':
            if shopify_id==None or shopify_id=='' or shopify_id=="":
                return Response({'message':'Empty hierarchy_id is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
            
            models.Shopify.objects.filter(user_id=tok1['user_id'],id=shop_id).update(api_token=api_token,shop_name=shop_name,display_name=display_name,updated_at=updated_at)
            click.cursor.execute(text(f'Drop Database if Exists \"{database}\"'))
            parent_ids=dshb_models.parent_ids.objects.get(id=shopify_id,parameter='shopify')
            message="Updated Successfully"
        else:
            pass
        click.client.query(f'Create Database if Not Exists \"{database}\"')
        result = click.json_to_table(api_urls,tok1,parent_ids.id,database,'shopify')
        if result['status']==200:
            data = {
                "message":message,
                "hierarchy_id":parent_ids.id,
                "connected":True
            }
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response({'message':str(result)},status=result['status'])
    else:
        return Response({'message':'Invalid Credentials'},status=response.status_code)
    


class shopify_authentication(CreateAPIView):
    serializer_class = serializers.shopify_serializer

    @csrf_exempt
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                parameter='SAVE'
                data=shopift_main(serializer,tok1,parameter)
                return data
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
        
    @csrf_exempt
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                parameter='UPDATE'
                data=shopift_main(serializer,tok1,parameter)
                return data
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
        

def shopify_data(id,table):
    pr_id=dshb_models.parent_ids.objects.get(id=id,parameter='shopify')
    shpo_tb=models.Shopify.objects.get(id=pr_id.table_id)
    dec_str=views.decode_string(shpo_tb.api_token)
    headers = {
        "X-Shopify-Access-Token": dec_str,
        "Content-Type": "application/json"
    }
    url = f"https://{str(shpo_tb.shop_name)}/admin/api/{str(shpo_tb.api_version)}/{str(table)}.json"
    response = requests.get(url, headers=headers)
    if response.status_code==200:
        data = response.json()
        d1 = {
            "data":data,
            "status":200
        }
    else:
        d1 = {
            "data":None,
            "status":400
        }
    return d1







