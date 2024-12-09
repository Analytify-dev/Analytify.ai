import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
from dashboard import views,models as dshb_models,columns_extract
from quickbooks import models,serializers as qb_seria,views as qb_views
import datetime
from datetime import timedelta
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
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR, Float, Boolean, DATETIME, DateTime, Date, DATE, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import json


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)


def query_details(user_id,query,qb_id,display_name):
    qb_id_1=columns_extract.parent_child_ids(qb_id,parameter="quickbooks")
    tokst=qb_views.status_check(user_id,qb_id_1)
    if tokst['status']==200:
        tokac=models.TokenStoring.objects.get(user=user_id,qbuserid=qb_id_1)
        if tokac.expiry_date > datetime.datetime.now(utc):
            pass
        else:
            rftk=qb_views.acess_refresh_token(tokac.refreshtoken,user_id,tokac.realm_id,qb_id_1)
            if rftk['status']==200:
                tokac = models.TokenStoring.objects.get(user=user_id,qbuserid=qb_id_1)
            else:
                st_dt={
                    "status":rftk['status'],
                    "data":rftk
                }
                return st_dt
        keys = qb_views.apis_keys()
        query = 'select * from '+str(query)
        api_url = "{}/v3/company/{}/query?query={}&minorversion=69".format(keys['api'],int(tokac.realm_id),query)
        headers = {
            'Authorization': f'Bearer {tokac.accesstoken}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = requests.request("GET", api_url, headers=headers)
        data = response.json()
        if response.status_code == 200:
            data1 = {
                "propertyquickbooksConnected":True,
                "status":data
            }
            # qb_file=qb_views.quickbooks_file_save(qb_id_1,data1,user_id,disp_name=display_name)
            # data1["qb_file_data"]=qb_file
            st_dt={
                "status":200,
                "data":data1,
                "qbuserid":tokac.qbuserid
            }
            return st_dt
        else:
            data1 = {
                "propertyquickbooksConnected":False,
                "status":data
            }
            st_dt={
                "status":response.status_code,
                "data":data1
            }
            return st_dt
    else:
        st_dt={
            "status":tokst['status'],
            "message":tokst
        }
        return st_dt


def balance_sheet(to_date,from_date,tokac):
    keys = qb_views.apis_keys()
    api_url = "{}/v3/company/{}/reports/BalanceSheet?end_date={}&start_date={}&minorversion=69".format(keys['api'],int(tokac.realm_id),to_date,from_date)
    account_data = {
        "end_date":str(to_date),
        "start_date":str(from_date)
    }
    headers = {
        'Authorization': f'Bearer {tokac.accesstoken}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = requests.request("GET", api_url, json=account_data, headers=headers)
    data = response.json()
    desired_key = 'ColData'
    results = qb_views.find_key_in_json(data, desired_key)
    if response.status_code == 200:
        data1 = {
            "propertyquickbooksConnected":True,
            # "Header":data['Header'],
            # "Columns":data['Columns'],
            # "results": results #data
        }
        # qb_file=qb_views.quickbooks_file_save(qb_id_1,data1,tok1['user_id'],disp_name="balance_sheet")
        # data1["qb_file_data"]=qb_file
        columns = data["Columns"]["Column"]
        metadata_values = [col["MetaData"][0]["Value"] for col in columns]
        col1_data = []
        col2_data = []
        for inner_list in results:
            if len(inner_list) > 0:  # Ensure there's at least one item
                col1_data.append(inner_list[0]["value"])  # First item 'value'
            if len(inner_list) > 1:  # Ensure there's at least a second item
                col2_data.append(inner_list[1]["value"])
        qb_views.table_create(str(tokac.qbuserid)+"_"+'balance_sheet',metadata_values[0],metadata_values[1],col1_data,col2_data)
        data1["table_name"]=str(tokac.qbuserid)+"_"+'balance_sheet'
        data1["status"]=200
        return data1
    else:
        data1 = {
                "propertyquickbooksConnected":False,
                "status":400,
                "data":data
            }
        return data1
    

def profit_loss(to_date,from_date,tokac):
    keys = qb_views.apis_keys()
    api_url = "{}/v3/company/{}/reports/ProfitAndLoss?start_date={}&end_date={}&minorversion=69".format(keys['api'],int(tokac.realm_id),from_date,to_date)
    # start_date must be less than end_date #YYYY-MM-DD format only.
    account_data = {
        "end_date":str(to_date),
        "start_date":str(from_date)
    }
    headers = {
        'Authorization': f'Bearer {tokac.accesstoken}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = requests.request("GET", api_url, json=account_data, headers=headers)
    data = response.json()
    desired_key = 'ColData'
    results = qb_views.find_key_in_json(data, desired_key)
    if response.status_code == 200:
        data1 = {
            "propertyquickbooksConnected":True,
            # "Header":data['Header'],
            # "Columns":data['Columns'],
            # "results": results   #data
        }
        # qb_file=qb_views.quickbooks_file_save(qb_id_1,data1,tok1['user_id'],disp_name="profit_and_loss")
        # data1["qb_file_data"]=qb_file
        columns = data["Columns"]["Column"]
        metadata_values = [col["MetaData"][0]["Value"] for col in columns]
        col1_data = []
        col2_data = []
        for inner_list in results:
            if len(inner_list) > 0:  # Ensure there's at least one item
                col1_data.append(inner_list[0]["value"])  # First item 'value'
            if len(inner_list) > 1:  # Ensure there's at least a second item
                col2_data.append(inner_list[1]["value"])
        qb_views.table_create(str(tokac.qbuserid)+"_"+'profit_and_loss',metadata_values[0],metadata_values[1],col1_data,col2_data)
        data1["table_name"]=str(tokac.qbuserid)+"_"+'profit_and_loss'
        data1["status"]=200
        return data1
    else:
        data1 = {
                "propertyquickbooksConnected":False,
                "status":400,
                "data":data
            }
        return data1
    

def account_details(tok1,qb_id):
    query='Account order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="account_details")
    if qr['status']==200:
        accounts = qr['data']['status']['QueryResponse']['Account']
        flattened_accounts = []
        for account in accounts:
            flattened_account = account.copy()
            flattened_account['MetaDataCreateTime'] = account['MetaData']['CreateTime']
            flattened_account['MetaDataLastUpdatedTime'] = account['MetaData']['LastUpdatedTime']
            flattened_account['CurrencyRefValue'] = account['CurrencyRef']['value']
            flattened_account['CurrencyRefName'] = account['CurrencyRef']['name']
            del flattened_account['MetaData']
            del flattened_account['CurrencyRef']
            flattened_accounts.append(flattened_account)
        table_cr=qb_views.create_user_qb_table(flattened_accounts,str(qr['qbuserid'])+"_"+'account_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'account_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])


def bill_details(tok1,qb_id):
    query='bill order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="bill_details")
    if qr['status']==200:
        bills = qr['data']['status']['QueryResponse']['Bill']
        flattened_bills = []
        for bill in bills:
            flattened_bill = bill.copy()
            flattened_bill['MetaDataCreateTime'] = bill['MetaData']['CreateTime']
            flattened_bill['MetaDataLastUpdatedTime'] = bill['MetaData']['LastUpdatedTime']
            flattened_bill['MetaDataLastModifiedByRef'] = bill['MetaData']['LastModifiedByRef']['value']
            flattened_bill['CurrencyRefValue'] = bill['CurrencyRef']['value']
            flattened_bill['CurrencyRefName'] = bill['CurrencyRef']['name']
            flattened_bill['VendorRefvalue'] = bill['VendorRef']['value']
            flattened_bill['VendorRefname'] = bill['VendorRef']['name']
            flattened_bill['APAccountRefvalue'] = bill['APAccountRef']['value']
            flattened_bill['APAccountRefname'] = bill['APAccountRef']['name']
            flattened_bill['TotalAmt'] = bill['TotalAmt']
            flattened_bills.append(flattened_bill)
        table_cr=qb_views.create_user_qb_table(flattened_bills,str(qr['qbuserid'])+"_"+'bill_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'bill_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])
    

def company_details(tok1,qb_id):
    query='CompanyInfo'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="company_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['CompanyInfo']
        flattened_bills = []
        for bill in bills:
            flattened_bill = bill.copy()
            flattened_bill['CustomerCommunicationEmailAddr'] = bill['CustomerCommunicationEmailAddr']['Address']
            flattened_bill['Email'] = bill['Email']['Address']
            flattened_bill['CreateTime'] = bill['MetaData']['CreateTime']
            flattened_bill['LastUpdatedTime'] = bill['MetaData']['LastUpdatedTime']
            flattened_bills.append(flattened_bill)
        table_cr=qb_views.create_user_qb_table(flattened_bills,str(qr['qbuserid'])+"_"+'company_details')
        if table_cr['status']==200:
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'company_details'
            qr["data"]["company_name"]=qr['data']['status']['QueryResponse']['CompanyInfo'][0]['LegalName']
            del qr['data']['status']
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])
    

def customer(tok1,qb_id):
    query='Customer order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="customer_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Customer']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'customer_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'customer_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])


def employee(tok1,qb_id):
    query='Employee order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="employee_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Employee']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'employee_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'employee_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])
    

def estimate(tok1,qb_id):
    query='estimate order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="estimate_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Estimate']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'estimate_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'estimate_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])



def invoice(tok1,qb_id):
    query='Invoice order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="invoice_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Invoice']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'invoice_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'invoice_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])


def item_details(tok1,qb_id):
    query='Item order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="items_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Item']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'item_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'item_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
        # return Response({'message':qr['message']},status=qr['status'])



def payment(tok1,qb_id):
    query='Payment order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="payment_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Payment']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'payment_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'payment_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
    

def preference(tok1,qb_id):
    query='Preferences'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="preference_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Preferences']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'preference_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'preference_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1


def tax_agency(tok1,qb_id):
    query='TaxAgency order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="tax_agency_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['TaxAgency']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'tax_agency_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'tax_agency_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
    

def vendor_details(tok1,qb_id):
    query='vendor order by Id desc'
    qr=query_details(tok1['user_id'],query,qb_id,display_name="vendor_details")
    if qr['status']==200:
        bills=qr['data']['status']['QueryResponse']['Vendor']
        table_cr=qb_views.create_user_qb_table(bills,str(qr['qbuserid'])+"_"+'vendor_details')
        if table_cr['status']==200:
            del qr['data']['status']
            qr["data"]["table_name"]=str(qr['qbuserid'])+"_"+'vendor_details'
            data1={
                "status":200,
                "data":qr['data']
            }
            return data1
        # return Response(qr['data'], status=status.HTTP_200_OK)
        else:
            data1={
                "status":table_cr['status'],
                "data":table_cr
            }
            return data1
            # return Response(table_cr,status=table_cr['status'])
    else:
        data1={
            "status":qr['status'],
            "data":qr['message']
        }
        return data1
#################################################################################################################################

##### Fetching BalanceSheet
class fetch_Balancesheet_details(CreateAPIView):
    serializer_class = qb_seria.filter_date

    def post(self,request,qb_id,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qb_id_1=columns_extract.parent_child_ids(qb_id,parameter="quickbooks")
            tokst=qb_views.status_check(tok1['user_id'],qb_id_1)
            if tokst['status']==200:
                tokac=models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
                if tokac.expiry_date > datetime.datetime.now(utc):
                    pass
                else:
                    rftk=qb_views.acess_refresh_token(tokac.refreshtoken,tok1['user_id'],tokac.realm_id,qb_id_1)
                    if rftk['status']==200:
                        tokac = models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
                    else:
                        return Response(rftk,status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    from_date = serializer.validated_data['from_date']
                    to_date = serializer.validated_data['to_date']
                    if from_date!='' and to_date!='':
                        if from_date < to_date:
                            pass
                        else:
                            return Response({"message":"Start Date Must Be Less Than End Date"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        pass
                    balance=balance_sheet(to_date,from_date,tokac)
                    if balance['status']==200:
                        return Response(balance, status=balance['status'])
                    else:
                        return Response(balance,status=balance['status'])
                else:
                    return Response({"message":"Serializer value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(tokst,status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(tok1,status=tok1['status'])



##### Fetching profitloss
class fetch_profitloss_details(CreateAPIView):
    serializer_class = qb_seria.filter_date

    def post(self,request,qb_id,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qb_id_1=columns_extract.parent_child_ids(qb_id,parameter="quickbooks")
            tokst=qb_views.status_check(tok1['user_id'],qb_id_1)
            if tokst['status']==200:
                tokac=models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
                if tokac.expiry_date > datetime.datetime.now(utc)+timedelta(hours=5,minutes=30):
                    pass
                else:
                    rftk=qb_views.acess_refresh_token(tokac.refreshtoken,tok1['user_id'],tokac.realm_id,qb_id_1)
                    if rftk['status']==200:
                        tokac = models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
                    else:
                        return Response(rftk,status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    from_date = serializer.validated_data['from_date']
                    to_date = serializer.validated_data['to_date']
                    if from_date!='' and to_date!='':
                        if from_date < to_date:
                            pass
                        else:
                            return Response({"message":"Start Date Must Be Less Than End Date"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        pass
                    profitloss=profit_loss(to_date,from_date,tokac)
                    if profitloss['status']==200:
                        return Response(profitloss, status=profitloss['status'])
                    else:
                        return Response(profitloss,status=profitloss['status'])
                else:
                    return Response({"message":"Serializer value error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(tokst,status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(tok1,status=tok1['status'])
        

        
##### Fetching Accounts
@api_view(['GET'])
def fetch_quickbooks_account(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=account_details(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)


##### Fetching Bills
@api_view(['GET'])
def fetch_Bill_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=bill_details(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        

##### Fetching company details
@api_view(['GET'])
def fetch_company_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=company_details(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching Customer Details
@api_view(['GET'])
def fetch_customer_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=customer(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)



##### Fetching Employee Details
@api_view(['GET'])
def fetch_employee_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=employee(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        


##### Fetching Estimate Details
@api_view(['GET'])
def fetch_estimate_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=estimate(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching Invoice Details
@api_view(['GET'])
def fetch_invoice_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=invoice(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching Item Details
@api_view(['GET'])
def fetch_item_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=item_details(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching Payment Details
@api_view(['GET'])
def fetch_payment_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=payment(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching Preferences Details
@api_view(['GET'])
def fetch_Preferences_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=preference(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### Fetching TaxAgency Details
@api_view(['GET'])
def fetch_TaxAgency_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=tax_agency(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

##### Fetching Vendors
@api_view(['GET'])
def fetch_vendor_details(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            accounts=vendor_details(tok1,qb_id)
            if accounts['status']==200:
                return Response(accounts, status=accounts['status'])
            else:
                return Response(accounts,status=accounts['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)