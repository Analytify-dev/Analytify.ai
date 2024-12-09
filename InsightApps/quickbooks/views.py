import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
from dashboard import views,models as dshb_models,Connections,columns_extract
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
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now(utc)+datetime.timedelta(minutes=60)

qb_urls = [
    "balance_sheet","profitandloss","Account","bill","CompanyInfo","Customer","Employee","estimate",
    "Invoice","Item","Payment","Preferences","TaxAgency","vendor"
]

def file_name_indexing(dis_names_list,comp_name):
    dis_names=[tk['display_name'] for tk in dis_names_list]
    cleaned_list1 = [re.sub(r'\s*\(.*?\)', '', filename) for filename in dis_names if filename is not None]
    cleaned_list = [filename.strip() for filename in cleaned_list1]
    name_di=comp_name
    if name_di in cleaned_list:
        count_s1 = cleaned_list.count(name_di)
        #### to add the no to file() based on the highest existing file no()
        filtered_files = [filename for filename in dis_names if isinstance(filename, str) and '(' in filename and ')' in filename]
        numbers = []
        for filename in filtered_files:
            match = re.search(r'\((\d+)\)', filename)
            if match:
                numbers.append(int(match.group(1)))
        highest_number = max(numbers) if numbers else None ## Fetch the highest no in file()
        if highest_number is not None or highest_number != None:
            fn_count=highest_number
        else:
            fn_count=count_s1
        final_dis_name = f'{name_di}({fn_count+1})'
    else:
        final_dis_name = name_di
    return final_dis_name


def quickbooks_token(sf_id,tok1):
    qb_id_1=columns_extract.parent_child_ids(sf_id,parameter="quickbooks")
    tokst=status_check(tok1['user_id'],qb_id_1)
    if tokst['status']==200:
        pass
    else:
        return Response({'message':tokst['message']},status=tokst['status'])
    tokac = models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
    if tokac.expiry_date > datetime.datetime.now(utc):
        data = {
            "data":tokac,
            "status":200
        }
        return data
    else:
        rftk=acess_refresh_token(tokac.refreshtoken,tok1['user_id'],tokac.realm_id,qb_id_1)
        if rftk['status']==200:
            tokac = models.TokenStoring.objects.get(user=tok1['user_id'],qbuserid=qb_id_1)
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
    
    
def normalize_data(record):
    normalized_record = {}
    if isinstance(record, dict):  # Check if record is indeed a dictionary
        for key, value in record.items():
            if isinstance(value, (dict, list)):  # Keep nested structures as is
                normalized_record[key] = value
            else:  # Convert everything else to string
                normalized_record[key] = str(value)
    else:
        print(f"Skipping non-dict record: {record}")  # Debug message if a non-dict is encountered
    return normalized_record


def create_user_qb_table(data1,table_name):
    try:
        # normalized_data = [normalize_data(record) for record in data1]
        # for record in normalized_data:
        #     if isinstance(record.get('details'), str):  # Check if 'details' is incorrectly a string
        #         record['details'] = {"info": record['details']}  # Convert to dictionary with a default key
        df = pd.DataFrame(data1)
        df = df.astype(str)
        columns_extract.file_check('check',file_name='quickbooks.db')
        try:
            engine = create_engine('sqlite:///quickbooks.db')
        except:
            columns_extract.file_check('remove',file_name='quickbooks.db')
            engine = create_engine('sqlite:///quickbooks.db')
        df.to_sql(str(table_name), con=engine, index=False, if_exists='replace')
        data = {
            "status":200
        }
        return data
    except Exception as e:
        data = {
            "status":400,
            "message":f'{str(e)}'
        }
        return data


def table_create(table_name,column1,column2,col1_data,col2_data):
    columns_extract.file_check('check',file_name='quickbooks.db')
    try:
        engine = create_engine('sqlite:///quickbooks.db', echo=True)
    except:
        columns_extract.file_check('remove',file_name='quickbooks.db')
        engine = create_engine('sqlite:///quickbooks.db', echo=True)

    Base = declarative_base()

    # class table_name(Base):
    #     __tablename__ = table_name  # Name of the table
    #     id = Column(Integer, primary_key=True)  # Primary key column
    #     column1 = Column(VARCHAR)
    #     column2 = Column(Float)

    attributes = {
        '__tablename__': table_name,  # Table name as a variable
        'id': Column(Integer, primary_key=True),  # Primary key column
        column1: Column(VARCHAR),  # Dynamic column 1
        column2: Column(Float)   # Dynamic column 2
    }
    table_sample = type('table_name', (Base,), attributes)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for d1,d2 in zip(col1_data,col2_data):
        if d1=='' or d1=="":
            d1=0
        elif d2=='' or d2=="":
            d2=0
        else:
            d1=d1
            d2=d2
        new_data = table_sample(**{column1: d1, column2: d2})
        session.add(new_data)
        session.commit()
    session.close()


def quickbooks_file_save(qb_id,data1,us_id,disp_name):
    if dshb_models.FileDetails.objects.filter(quickbooks_user_id=qb_id,display_name=disp_name).exists():
        qbmod=dshb_models.FileDetails.objects.get(quickbooks_user_id=qb_id,display_name=disp_name)
        # pattern = r'/insightapps/(.*)'
        # match = re.search(pattern, qbmod.source)
        # dl_key12 = match.group(1)
        # dl_key = re.sub(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', '', str(dl_key12))
        dl_key=qbmod.datapath
    else:
        dl_key=""

    ip='files/quickbooks'
    fl_tp=dshb_models.FileType.objects.get(file_type="QUICKBOOKS")
    normalized_data = [normalize_data(record) for record in data1]
    files=Connections.file_save_1(normalized_data,qb_id,us_id,ip,str(dl_key))
    if dshb_models.FileDetails.objects.filter(quickbooks_user_id=qb_id,display_name=disp_name).exists():
        dshb_models.FileDetails.objects.filter(quickbooks_user_id=qb_id,display_name=disp_name).update(source=files['file_url'],updated_at=updated_at,datapath=files['file_key'])
        qbmod=dshb_models.FileDetails.objects.get(quickbooks_user_id=qb_id,display_name=disp_name)
    else:
        qbmod=dshb_models.FileDetails.objects.create(quickbooks_user_id=qb_id,display_name=disp_name,source=files['file_url'],
                                                uploaded_at=created_at,updated_at=updated_at,user_id=us_id,datapath=files['file_key'],
                                                file_type=fl_tp.id)
    data = {
        "qb_user_id":qbmod.quickbooks_user_id,
        "file_id":qbmod.id,
        "qb_display_name":qbmod.display_name
    }
    return data
            

def find_key_in_json(data, target_key, results=None):
    if results is None:
        results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                results.append(value)
            elif isinstance(value, (dict, list)):
                find_key_in_json(value, target_key, results)
    elif isinstance(data, list):
        for item in data:
            find_key_in_json(item, target_key, results)

    return results

def status_check(user_id,qb_id):
    if models.TokenStoring.objects.filter(user=user_id,qbuserid=qb_id).exists():
        data = {
            "status":200,
            "quickbooksConnected":True
        }
    else:
        data = {
            "status":400,
            "message":"please login again in quickbooks",
            "quickbooksConnected":False
        }
    return data


def apis_keys():
    env = settings.ENVIRONMENT
    if env=='sandbox':
        client_id = settings.SANDBOX_QUICKBOOKS_ID
        client_secret = settings.SANDBOX_QUICKBOOKS_SECRET
        redirect_uri = settings.SANDBOX_REDIRECT_URL
        scopes = settings.SANDBOX_SCOPES
        api = settings.SANDBOX_URL
    elif env=='production':
        client_id = settings.PRODUCTION_QUICKBOOKS_ID
        client_secret = settings.PRODUCTION_QUICKBOOKS_SECRET
        redirect_uri = settings.PROPERTY_SANDBOX_REDIRECT_URL
        scopes = settings.PRODUCTION_SCOPES
        api = settings.PRODUCTION_URL
    else:
        return Response({"message":"Not Acceptable"},status=status.HTTP_400_BAD_REQUEST)
    data = {
        "client_id":client_id,
        "client_secret":client_secret,
        "redirect_uri":redirect_uri,
        "scopes":scopes,
        "api":api
    }
    return data



def token_create(redirect_response,user_id,realm_id): #,display_name
    try:
        keys = apis_keys()
        oauth = OAuth2Session(keys['client_id'], redirect_uri=keys['redirect_uri'], scope=keys['scopes'])
        token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        token = oauth.fetch_token(token_url, authorization_response=redirect_response, auth=HTTPBasicAuth(keys['client_id'], keys['client_secret']))
        models.TokenStoring.objects.filter(user=user_id,token_code=redirect_response).delete()
        tb = models.TokenStoring.objects.create(tokentype=token['token_type'],accesstoken=token['access_token'],refreshtoken=token['refresh_token'],
                                                idtoken=token['id_token'],updated_at=updated_at,created_at=created_at,expiry_date=expired_at,user=user_id,realm_id=realm_id,
                                                parameter="quickbooks",token_code=redirect_response) #,display_name=display_name
        quid = 'QB_'+str(tb.id)+str(tb.user)
        models.TokenStoring.objects.filter(id=tb.id).update(qbuserid=quid)
        parent_ids=dshb_models.parent_ids.objects.create(table_id=tb.id,parameter="quickbooks")
        tok1={}
        tok1["user_id"]=user_id
        comp_info=endpoints_data.company_details(tok1,parent_ids.id)
        tk_cmp_tb=models.TokenStoring.objects.filter(user=user_id,parameter='quickbooks').values()
        comp_name = comp_info['data']['company_name']
        final_dis_name = file_name_indexing(tk_cmp_tb,comp_name)
        models.TokenStoring.objects.filter(id=tb.id).update(display_name=final_dis_name)
        data = {
            "status":200,
            "quickbooks_id":parent_ids.id,            #tb.qbuserid,
            "message":"Success",
            "quickbooksConnected":True,
            "accesstoken":token['access_token']
        }
        return data
    except:
        data = {
            "status":400,
            "message":"please login again in quickbooks",
            "quickbooksConnected":False,
        }
        return data
        


def acess_refresh_token(refresh_token,user_id,realm_id,qb_id):
    keys = apis_keys()
    token_endpoint = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': keys['client_id'],
        'client_secret': keys['client_secret'],
        'realm_id':realm_id
    }
    response = requests.post(token_endpoint, data=data)
    token_data = response.json()
    if response.status_code == 200:
        # new_access_token = token_data.get('access_token')
        models.TokenStoring.objects.filter(user=user_id,qbuserid=qb_id).update(accesstoken=token_data['access_token'],refreshtoken=token_data['refresh_token'],created_at=created_at,expiry_date=expired_at,realm_id=realm_id)
        tk1=models.TokenStoring.objects.get(qbuserid=qb_id)
        parent_ids=dshb_models.parent_ids.objects.get(table_id=tk1.id,parameter='quickbooks')
        data = {
            "status":200,
            "quickbooks_id":parent_ids.id,
            "message":"Success",
            "quickbooksConnected":True,
            "accesstoken":token_data['access_token']
        }
        return data
    else:
        data = {
            "status":400,
            "quickbooksConnected":False,
            "message":token_data,
            "message_status":"please login to quickbboks for token"
        }
        return data


@api_view(['GET'])
def authentication_quickbooks(request,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            keys = apis_keys()
            authorization_base_url = 'https://appcenter.intuit.com/connect/oauth2'
            oauth = OAuth2Session(keys['client_id'], redirect_uri=keys['redirect_uri'], scope=keys['scopes'])
            authorization_url, state= oauth.authorization_url(authorization_base_url)
            data = {
                "redirection_url":authorization_url
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##### GET the token from reirect url
class token_api(CreateAPIView):
    serializer_class = serializers.token_serializer

    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                redirect_response1 = serializer.validated_data['redirect_url']
                # display_name = serializer.validated_data['display_name']
                # r1 = settings.token_url
                str12 = 'https://demo.insightapps.ai'
                redirect_response = str(str12)+str(redirect_response1)
                parsed_url = urlparse(redirect_response)
                query_params = parse_qs(parsed_url.query)
                realm_id = query_params.get('realmId', [None])[0]
                parameter="quickbooks"
                # if models.TokenStoring.objects.filter(user=tok1['user_id'],display_name=display_name,parameter=parameter).exists():
                #     return Response({'message':'Display name already exists, please change display name'},status=status.HTTP_406_NOT_ACCEPTABLE)
                ac_token=token_create(redirect_response,tok1['user_id'],realm_id) #,display_name
                if ac_token['status']==200:
                    return Response(ac_token,status=status.HTTP_200_OK)
                elif ac_token['status']==400:
                    if models.TokenStoring.objects.filter(user=tok1['user_id'],parameter=parameter,token_code=redirect_response).exists(): #,display_name=display_name
                        tokac = models.TokenStoring.objects.get(user=tok1['user_id'],parameter=parameter,token_code=redirect_response) #,display_name=display_name
                        if tokac.expiry_date < datetime.datetime.now(utc):#+datetime.timedelta(hours=5,minutes=30)
                            refer = acess_refresh_token(tokac.refreshtoken,tok1['user_id'],realm_id,tokac.qbuserid)
                            if refer['status']==200:
                                return Response(refer,status=status.HTTP_200_OK)
                            else:
                                return Response(refer,status=status.HTTP_400_BAD_REQUEST)
                        else:
                            tk1=models.TokenStoring.objects.get(qbuserid=tokac.qbuserid)
                            parent_ids=dshb_models.parent_ids.objects.get(table_id=tk1.id,parameter='quickbooks')
                            return Response({"message":"Success","quickbooksConnected":True,"quickbooks_id":parent_ids.id},status=status.HTTP_200_OK)
                    else:
                        return Response({'message':'token not exists, please login again'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(ac_token,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"Serializer value error"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])


##### Disconnection quickbooks 

@api_view(['DELETE'])
def qb_disconnection(request,qb_id,token):
    if request.method=='DELETE':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            qb_id_1=columns_extract.parent_child_ids(qb_id,parameter="quickbooks")
            tokst=status_check(tok1['user_id'],qb_id_1)
            if tokst['status']==200:
                models.TokenStoring.objects.filter(user=tok1['user_id'],qbuserid=qb_id).delete()
                dshb_models.FileDetails.objects.filter(quickbooks_user_id=qb_id).delete()
                dshb_models.parent_ids.objects.filter(id=qb_id).delete()
                # delete sheet, dashbaord, queries also.
                return Response({"message":"Disconnected from quickbooks","quickbooksConnected":False},status=status.HTTP_200_OK)
            else:
                return Response(tokst,status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

###### GET user details from quickbooks ###
@api_view(['GET'])
def get_quickbooks_user_info(request,qb_id,token):##
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            tokst=quickbooks_token(qb_id,tok1)
            if tokst['status']==200:
                tokac=tokst['data']
            else:
                return Response({'message':'session expired, login to quickbooks again',"quickbooksConnected":False,},status=tokst['status'])
            if settings.ENVIRONMENT == 'sandbox':
                url = 'https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo'
            else:
                url = 'https://accounts.platform.intuit.com/v1/openid_connect/userinfo'
            headers = {
                'Authorization': f'Bearer {tokac.accesstoken}',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers)
            if response.status_code==200:
                return Response({'message':'success','data':response.json()},status=status.HTTP_200_OK)
            else:
                return response({'message':response.json()},status=response.status_code)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


@api_view(['GET'])
def qb_data_reload(request,qb_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            tokst=quickbooks_token(qb_id,tok1)
            if tokst['status']==200:
                tokac=tokst['data']
            else:
                return Response({'message':'session expired, login to quickbooks again',"quickbooksConnected":False,},status=tokst['status'])
            to_date=""
            from_date=""
            try:
                endpoints_data.balance_sheet(to_date,from_date,tokac)
                endpoints_data.profit_loss(to_date,from_date,tokac)
                endpoints_data.account_details(tok1,qb_id)
                endpoints_data.bill_details(tok1,qb_id)
                endpoints_data.company_details(tok1,qb_id)
                endpoints_data.customer(tok1,qb_id)
                endpoints_data.employee(tok1,qb_id)
                endpoints_data.estimate(tok1,qb_id)
                endpoints_data.invoice(tok1,qb_id)
                endpoints_data.item_details(tok1,qb_id)
                endpoints_data.payment(tok1,qb_id)
                endpoints_data.preference(tok1,qb_id)
                endpoints_data.tax_agency(tok1,qb_id)
                endpoints_data.vendor_details(tok1,qb_id)
            except Exception as e:
                return Response({'message':'Incomplete data reloading/Error'},status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({"message":"Method not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

def quickbooks_query_data(server_id,tok1,tabl_name):
    token_status=quickbooks_token(server_id,tok1)
    if token_status['status']==200:
        tokac=token_status['data']
    else:
        return Response({'message':'session expired, login to quickbooks again',"quickbooksConnected":False,},status=token_status['status'])
    keys = apis_keys()
    to_date=""
    from_date=""
    account_data = {
        "end_date":str(to_date),
        "start_date":str(from_date)
    }
    headers = {
        'Authorization': f'Bearer {tokac.accesstoken}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    query = 'select * from '+str(tabl_name)+' order by Id desc'
    if tabl_name=="balance_sheet":
        api_url = "{}/v3/company/{}/reports/BalanceSheet?end_date={}&start_date={}&minorversion=69".format(keys['api'],int(tokac.realm_id),to_date,from_date)
    elif tabl_name=="profitandloss":
        api_url = "{}/v3/company/{}/reports/ProfitAndLoss?start_date={}&end_date={}&minorversion=69".format(keys['api'],int(tokac.realm_id),from_date,to_date)
    else:
        api_url = "{}/v3/company/{}/query?query={}&minorversion=69".format(keys['api'],int(tokac.realm_id),query)
    
    response = requests.request("GET", api_url, json=account_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return Response(data,status=status.HTTP_200_OK)
    else:
        return Response({'message':'session expired, login to quickbooks again',"quickbooksConnected":False,},status=token_status['status'])
