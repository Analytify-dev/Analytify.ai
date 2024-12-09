import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
import pkce,base64,hashlib
from dashboard import views,columns_extract
from quickbooks import models,serializers,endpoints_data,views as qb_views
from dashboard import models as dshb_models
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
from django.shortcuts import redirect


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now(utc)+datetime.timedelta(minutes=60)


salesforce_tables= ['Account', 'Address', 'Announcement', 'AppMenuItem', 'Asset', 'Attachment', 'Campaign', 'Case', 'Group', 'Contact',
                     'Contract', 'Dashboard', 'Document', 'Domain', 'EmailCapture', 'Entitlement', 'Event', 'FileSearchActivity', 
                     'Folder', 'Group', 'Holiday', 'Idea', 'Individual', 'Lead', 'Location', 'Macro', 'Name', 'Note', 'Opportunity', 
                     'Order', 'Organization', 'Partner', 'Period', 'Profile', 'Publisher', 'RecordAction', 'Report', 'SearchActivity',
                       'Shipment', 'Site', 'Site', 'Skill', 'Solution', 'Stamp', 'Survey', 'Task', 'Topic', 'User', 
                       'UserAppMenuCustomization', 'Vote']


def apis_keys():
    client_id = settings.SALESFORCE_CONSUMER_KEY
    client_secret = settings.SALESFORCE_CONSUMER_SECRET
    redirect_uri = settings.SALESFORCE_REDIRECT_URI
    auth_url = settings.SALESFORCE_AUTH_URL
    toke_url = settings.SALESFORCE_TOKEN_URL
    domain_url = settings.SALESFORCE_DOMAIN
    data = {
        "client_id":client_id,
        "client_secret":client_secret,
        "redirect_uri":redirect_uri,
        "auth_url":auth_url,
        "tok_url":toke_url,
        "domain_url":domain_url
    }
    return data

def sf_status_check(user_id,qb_id):
    if models.TokenStoring.objects.filter(user=user_id,salesuserid=qb_id).exists():
        data = {
            "status":200,
            "Salesforceconnected":True
        }
    else:
        data = {
            "status":400,
            "message":"please login again in salesforce",
            "Salesforceconnected":False
        }
    return data


def token_create(code,keys,user_id,redirect_response,parameter,domain): #display_name
    try:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': keys['client_id'],
            'client_secret': keys['client_secret'],
            'redirect_uri': keys['redirect_uri']
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(keys['tok_url'], data=data, headers=headers)
        if response.status_code==200:
            token=response.json()
            # models.TokenStoring.objects.filter(user=user_id,parameter=parameter).delete()#display_name=display_name,
            tb = models.TokenStoring.objects.create(tokentype=token['token_type'],accesstoken=token['access_token'],refreshtoken=token['refresh_token'],
                                                    idtoken=token['id_token'],updated_at=updated_at,created_at=created_at,expiry_date=expired_at,user=user_id,
                                                    parameter=parameter,token_code=redirect_response) #,display_name=display_name
            sfid = 'SF_'+str(tb.id)+str(tb.user)
            models.TokenStoring.objects.filter(id=tb.id).update(salesuserid=sfid)
            parent_ids=dshb_models.parent_ids.objects.create(table_id=tb.id,parameter="salesforce")
            url = f"{str(domain)}/services/oauth2/userinfo"
            headers = {
                'Authorization': f'Bearer {str(tb.accesstoken)}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers)
            if response.status_code==200:
                data12=response.json()
                tk_cmp_tb=models.TokenStoring.objects.filter(user=user_id,parameter='salesforce').values()
                comp_name = data12['preferred_username']
                final_dis_name = qb_views.file_name_indexing(tk_cmp_tb,comp_name)
                models.TokenStoring.objects.filter(id=tb.id).update(display_name=final_dis_name)
                data = {
                    "status":200,
                    "salesforce_id":parent_ids.id,       #tb.salesuserid
                    "message":"Success",
                    "SalesforceConnected":True,
                    "accesstoken":token['access_token']
                }
                return data
        else:
            data = {
                "status":response.status_code,
                "message":response.json()
            }
            return data
    except:
        data = {
            "status":400,
            "message":"please login again in salesforce",
            "SalesforceConnected":False,
        }
        return data



def token_access_refresh(sf_id,user_id):
    keys = apis_keys()
    qb_id_1=columns_extract.parent_child_ids(sf_id,parameter="salesforce")
    tokac=models.TokenStoring.objects.get(user=user_id,salesuserid=qb_id_1)
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': tokac.refreshtoken,
        'client_id': keys['client_id'],
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(keys['tok_url'], data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        models.TokenStoring.objects.filter(user=user_id,salesuserid=qb_id_1).update(accesstoken=token_data['access_token'],refreshtoken=token_data['refresh_token'],created_at=created_at,expiry_date=expired_at)
        tk1=models.TokenStoring.objects.get(salesuserid=qb_id_1)
        parent_ids=dshb_models.parent_ids.objects.get(table_id=tk1.id,parameter='salesforce')
        data = {
            "status":200,
            "salesforce_id":parent_ids.id,
            "message":"Success",
            "salesforceConnected":True,
            "accesstoken":token_data['access_token']
        }
        return data
    else:
        data = {
            "status":400,
            "salesforceConnected":False,
            "message":response,
            "message_status":"please login to salesforce for token"
        }
        return data

# def callback_api(request):
#     code = request.GET.get('code')
#     if code:
#         # Redirect to a route that will handle the token exchange
#         return redirect(f'/token_fetch/?code={code}')
#     # return HttpResponse("Error: No code found in request.", status=400)


class callback_api(CreateAPIView):
    serializer_class=serializers.display_name

    @transaction.atomic
    def post(self,request,token):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            redirect_url2=serializer.validated_data['redirect_url']
            redirect_url1=str(redirect_url2).replace("?","/?")
            str12 = 'https://demo.insightapps.ai'
            redirect_url = str(str12)+str(redirect_url1)
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            code = query_params.get('code', [None])[0]
            tok1 = views.test_token(token)
            if tok1['status']==200:
                keys = apis_keys()
                parameter="salesforce"
                token=token_create(code,keys,tok1['user_id'],redirect_url,parameter="salesforce",domain=keys['domain_url'])#,display_name
                if token['status']==200:
                    return Response(token,status=status.HTTP_200_OK)
                elif token['status']==400:
                    if models.TokenStoring.objects.filter(user=tok1['user_id'],parameter=parameter,token_code=redirect_url).exists(): #,display_name=display_name
                        tokac = models.TokenStoring.objects.get(user=tok1['user_id'],parameter=parameter,token_code=redirect_url) #,display_name=display_name
                        parent_ids=dshb_models.parent_ids.objects.get(table_id=tokac.id)
                        if tokac.expiry_date < datetime.datetime.now(utc):#+datetime.timedelta(hours=5,minutes=30)
                            refer = token_access_refresh(tokac.salesuserid,tok1['user_id'])
                            if refer['status']==200:
                                return Response(refer,status=status.HTTP_200_OK)
                            else:
                                return Response(refer,status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"message":"Success","salesforce_id":parent_ids.id,"SalesforceConnected":True},status=status.HTTP_200_OK)
                    else:
                        return Response({'message':'token not exists, please login again'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(token,status=token['status'])
            else:
                return Response(tok1,status=tok1['status'])
        else:
            return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def authentication_salesforce(request,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            keys = apis_keys()
            params = {
                'response_type': 'code',
                'client_id': keys['client_id'],
                'redirect_uri': keys['redirect_uri'],
                # 'scope':'full'
                'scope': 'offline_access full'
            }
            login_url = f"{keys['auth_url']}?{urllib.parse.urlencode(params)}"
            data = {
                "redirection_url":login_url
            }
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET'])
def refresh_access_token(request,sf_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            refresh=token_access_refresh(sf_id,tok1['user_id'])
            if refresh['status']==200:
                return Response(refresh,status=status.HTTP_200_OK)
            else:
                return Response(refresh,status=refresh['status'])
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)




##### Disconnection salesforce 

@api_view(['DELETE'])
def qb_salesforce(request,sf_id,token):
    if request.method=='DELETE':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qb_id_1=columns_extract.parent_child_ids(sf_id,parameter="salesforce")
            tokst=sf_status_check(tok1['user_id'],qb_id_1)
            if tokst['status']==200:
                models.TokenStoring.objects.filter(user=tok1['user_id'],salesuserid=sf_id).delete()
                # dshb_models.FileDetails.objects.filter(quickbooks_user_id=qb_id).delete()
                dshb_models.parent_ids.objects.filter(id=sf_id).delete()
                # delete sheet, dashbaord, queries also.
                return Response({"message":"Disconnected from salesforce","Salesforceconnected":False},status=status.HTTP_200_OK)
            else:
                return Response(tokst,status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)