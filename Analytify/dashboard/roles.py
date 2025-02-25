import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
from dashboard import views,serializers,models,authentication,previlages,Connections
import datetime
from io import BytesIO
from pytz import utc
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
from django.core.mail import send_mail
import threading
from oauth2_provider.models import AccessToken, RefreshToken, Grant


created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)


def get_previlage_id(previlage):
    rol_lst=[]
    for previ in previlage:
        prvg=models.previlages.objects.get(previlage=previ)
        rl_list=[]
        roles=models.Role.objects.filter(previlage_id__contains=prvg.id).values('role_id')
        for rl in roles:
            rl_list.append(rl['role_id'])
        # rl_ls = [rl['role_id'] for rl in roles]
        rol_lst.append(rl_list)
    role_list=[item for sublist in rol_lst for item in sublist]
    final_list=list(set(role_list))
    return final_list


def role_status(token,rl_id):
    tok12 = views.test_token(token)
    # if tok12['status']==200 and list(filter(lambda x: x['role_id'] in rl_id, [tok12]))!=[]:
    if tok12['status']==200 and list(filter(lambda x: x in tok12['role_id'], rl_id))!=[]:
        data = {
            "status":200,
            # "tok1":{
            "role_id":tok12['role_id'],
            "user_id":tok12['user_id'],
            "usertable":tok12['usertable'],
            "username":tok12['username'],
            "email":tok12['email']
            # }
        }
        return data
    elif tok12['status']==200 and list(filter(lambda x: x['role_id'] in rl_id, [tok12]))==[]:
        data = {
            "status":401,
            # "tok1":{
            "message":"User Not assigned to this ROLE/Not Assigned"
            # }
        }
        return data
    else:
        data = {
            "status":400,
            # "tok1":{
            "message":tok12['message']
            # }
        }
        return data
    

def TM_mail_SMTP_mail(username,password,created_by,supportemail,email):  ##liscence
    try:
        context = {'username':username,'E_mail':email,'password':password,'created_by':created_by,'supportemail':supportemail,'IP':settings.link_url}  ##'liscence':liscence,
        html_message = render_to_string('role.html', context)
        message = '{} Joined successfully'.format(username)
        subject = "{} Joining".format(username)
        from_email = settings.EMAIL_HOST_USER
        to_email = [email.lower()]
        send_mail(subject, message, from_email, to_email, html_message=html_message)
        data = {
            "status":200,
            "message" : "Account Activation Email Sent",
        }
        return data
    except :
        data = {
            "status":400,
            "message":"SMTP Error"
        }
        return data


class previlages_get(CreateAPIView):
    serializer_class=serializers.search_serializer

    @transaction.atomic
    def put(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.view_previlages])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                search = serializer.validated_data['search']
                pr_list=[]
                if search=='' or search==None:
                    prev=models.previlages.objects.all().values()
                else:
                    prev=models.previlages.objects.filter(previlage__icontains=search).values()
                for i1 in prev:
                    pr_list.append({"id":i1['id'],
                    "previlage":i1['previlage']})
                return Response(pr_list,status=status.HTTP_200_OK)
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
    
def role_create_status(role_name,previlages):
    if role_name=='' or role_name==None or role_name==' ' or role_name=="":
        return Response({'message':'empty role name field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif previlages=='' or previlages==[] or previlages=="" or previlages==None:
        return Response({'message':'empty previlages field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return 200


class add_role(CreateAPIView):
    serializer_class=serializers.role_seri

    @transaction.atomic
    def post(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.create_roles,previlages.view_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                role_name12 = serializer.validated_data['role_name']
                role_description = serializer.validated_data['role_description']
                previlages_ids = serializer.validated_data['previlages']
                if models.Role.objects.filter(role__exact=role_name12,created_by=tok1['user_id']).exists():
                    return Response({'message':'Role already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    # for prid in ast.literal_eval(previlages):
                    # for prid in previlages:
                    rl_data=role_create_status(role_name12,previlages_ids)
                    if rl_data==200:
                        pass
                    else:
                        return rl_data
                    rlct=models.Role.objects.create(role=role_name12,role_desc=role_description,created_by=tok1['user_id'],previlage_id=previlages_ids,
                                                created_at=created_at,updated_at=updated_at)
                    rlct.save()
                    models.Role.objects.filter(role_id=rlct.role_id).update(created_at=created_at,updated_at=updated_at)
                    return Response({'message':'Role created successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        
class list_of_roles(CreateAPIView):
    serializer_class=serializers.search_serializer

    @transaction.atomic
    def put(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.view_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                search=serializer.validated_data['search']
                page_no=serializer.validated_data['page_no']
                page_count=serializer.validated_data['page_count']
                if search=='' or search==None:
                    rol_pr=models.Role.objects.filter(created_by=tok1['user_id']).values().order_by('-updated_at')
                else:
                    rol_pr=models.Role.objects.filter(created_by=tok1['user_id'],role__icontains=search).values().order_by('-updated_at')
                final_list=[]
                prev_name_li=[]
                for role in rol_pr:
                    for i3 in ast.literal_eval(role['previlage_id']):
                        prev_name=models.previlages.objects.get(id=i3)
                        prev_name_li.append(prev_name.previlage)
                    data = {
                        "role_id":role['role_id'],
                        "created_by":tok1['username'],
                        "role":role['role'],
                        "previlages":prev_name_li,
                        "updated_at":role['updated_at'].date(),
                        "created_at":role['created_at'].date()
                    }  
                    final_list.append(data)   
                try:
                    resul_data=Connections.pagination(request,final_list,page_no,page_count)
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({'message':'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)  
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        
    
    @transaction.atomic
    def get(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.view_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            roles_list=models.Role.objects.filter(created_by=tok1['user_id']).values('role').order_by('-updated_at')
            roleslist=[rl['role'] for rl in roles_list]
            return Response(roleslist,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])


def user_status(firstname,lastname,username,email,password,conformpassword,role):
    if firstname=='' or firstname==None or firstname==' ' or firstname=="":
        return Response({'message':'empty firstname field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif lastname=='' or lastname==None or lastname==' ' or lastname=="":
        return Response({'message':'empty lastname field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif username=='' or username==None or username==' ' or username=="":
        return Response({'message':'empty username field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif email=='' or email==None or email==' ' or email=="":
        return Response({'message':'empty email field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif password=='' or password==None or password==' ' or password=="":
        return Response({'message':'empty password field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    elif conformpassword=='' or conformpassword==None or conformpassword==' ' or conformpassword=="":
        return Response({'message':'empty conformpassword field is not acceptable'},status=status.HTTP_406_NOT_ACCEPTABLE)
    # elif role=='' or role==[] or role=="" or role==None:
    #     return Response({'message':'empty role field is not acceptable, User had atleast one role'},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return 200


class create_user_role(CreateAPIView):
    serializer_class=serializers.adding_user_serializer

    @transaction.atomic
    def post(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.create_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                firstname = serializer.validated_data['firstname']
                lastname = serializer.validated_data['lastname']
                username = serializer.validated_data['username']
                email = serializer.validated_data['email']
                active = serializer.validated_data['is_active']
                password = serializer.validated_data['password']
                conformpassword = serializer.validated_data['conformpassword']
                role = serializer.validated_data['role']
                us_table=user_status(firstname,lastname,username,email,password,conformpassword,role)
                if models.UserProfile.objects.filter(username=username).exists():
                    return Response({"message": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
                elif models.UserProfile.objects.filter(email__iexact=email).exists():
                    return Response({"message": "email already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                elif us_table==200:
                    pass
                else:
                    return us_table
                if active==None or active=='':
                    active=False
                else:
                    active=active
                pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"
                r= re.findall(pattern,password)
                if not r:
                    return Response({"message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."},status=status.HTTP_406_NOT_ACCEPTABLE)
                elif password!=conformpassword:
                    return Response({"message":"Password did not matched"},status=status.HTTP_406_NOT_ACCEPTABLE)
                # liscence_key = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(300)))
                tm_mail=TM_mail_SMTP_mail(username,password,tok1['username'],tok1['email'],email=email)  ##liscence_key
                if tm_mail['status']==200:
                    pass
                else:
                    return Response(tm_mail,status=status.HTTP_400_BAD_REQUEST)
                up_tb=models.UserProfile.objects.create_user(username=username,name=username,password=password,email=email,created_at=created_at,updated_at=updated_at,first_name=firstname,last_name=lastname,is_active=active)
                models.UserProfile.objects.filter(id=up_tb.id).update(created_at=created_at,updated_at=updated_at)
                if role==[] or role=='':
                    rtb=models.UserRole.objects.create(user_id=up_tb.id,created_by=tok1['user_id'])
                    models.UserRole.objects.filter(id=rtb.id).update(created_at=created_at,updated_at=updated_at)
                else:
                    for i21 in role:
                        if models.Role.objects.filter(created_by=tok1['user_id'],role=i21).exists():
                            role_tb=models.Role.objects.get(created_by=tok1['user_id'],role=i21)
                            rtb=models.UserRole.objects.create(role_id=role_tb.role_id,user_id=up_tb.id,created_by=tok1['user_id'],created_at=created_at,updated_at=updated_at)
                            models.UserRole.objects.filter(id=rtb.id).update(created_at=created_at,updated_at=updated_at)
                        else:
                            return Response({'message':'Role not exists for this User'},status=status.HTTP_404_NOT_FOUND)
                user_id=up_tb.id
                thread = threading.Thread(target=authentication.signup_thread, args=(user_id,))
                thread.start()
                # models.license_key.objects.filter(user_id=up_tb.id).delete()
                # models.license_key.objects.create(user_id=up_tb.id,max_limit=settings.db_connections,key=liscence_key,created_at=created_at,updated_at=updated_at,is_validated=True)
                return Response({'message':'created successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        


class get_user_role(CreateAPIView):
    serializer_class=serializers.search_serializer

    @transaction.atomic
    def put(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.view_user,previlages.view_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                search=serializer.validated_data['search']
                page_no=serializer.validated_data['page_no']
                page_count=serializer.validated_data['page_count']
                # rol_tb=models.Role.objects.filter(created_by=tok1['user_id']).values('role_id','role')
                # role_ids=[role['role_id'] for role in rol_tb]
                # role1=[role['role'] for role in rol_tb]
                user=[]
                # for rl,role in zip(role_ids,role1):
                up_tb=models.UserRole.objects.filter(created_by=tok1['user_id']).values().order_by('-updated_at')
                user_ids=[usid['user_id'] for usid in up_tb]
                for us_id in user_ids:
                    if search=='' or search==None:
                        final_user=models.UserProfile.objects.filter(id=us_id).values().order_by('-updated_at')
                    else:
                        final_user=models.UserProfile.objects.filter(id=us_id,username__icontains=search).values().order_by('-updated_at')
                    for i2 in final_user:
                        data = {
                            "user_id":i2['id'],
                            "name":i2['username'],
                            "username":i2['username'],
                            "email":i2['email'],
                            "is_active":i2['is_active'],
                            "created_by":tok1['username'],
                            "created_at":i2['created_at'].date(),
                            "updated_at":i2['updated_at'].date(),
                            # "role":roles,
                        }
                        user.append(data)
                #### Removing duplicates based on user_id
                unique_sheets = []
                seen_usernames = set()
                for sheet in user:
                    if sheet['user_id'] not in seen_usernames:
                        unique_sheets.append(sheet)
                        seen_usernames.add(sheet['user_id'])
                try:
                    resul_data=Connections.pagination(request,unique_sheets,page_no,page_count)
                    return Response(resul_data,status=status.HTTP_200_OK)
                except:
                    return Response({'message':'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST) 
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])

    

@api_view(['DELETE'])
def delete_user(request,userid,token):
    if request.method=='DELETE':
        role_list=get_previlage_id(previlage=[previlages.delete_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            if models.UserRole.objects.filter(user_id=userid).exists():
                if models.UserRole.objects.filter(user_id=userid,created_by=tok1['user_id']).exists():
                    try:
                        Grant.objects.filter(user_id=userid).delete()
                        AccessToken.objects.filter(user_id=userid).delete()
                        RefreshToken.objects.filter(user_id=userid).delete()
                        models.UserProfile.objects.filter(id=userid).delete()
                    except:
                        return Response({'message':'Table not exist'},status=status.HTTP_404_NOT_FOUND)
                    # models.license_key.objects.filter(user_id=userid).delete()
                    models.ServerDetails.objects.filter(user_id=userid).delete()
                    models.FileDetails.objects.filter(user_id=userid).delete()
                    models.UserRole.objects.filter(user_id=userid).delete()
                    file=models.FileDetails.objects.filter(user_id=userid).values()
                    for fl_id in file:
                        qr_list=models.QuerySets.objects.filter(file_id=fl_id['id']).values()
                        for qr_id in qr_list:
                            Connections.delete_data(qr_id['queryset_id'],qr_id['server_id'],userid)
                        models.FileDetails.objects.filter(id=fl_id['id'],user_id=userid).delete()
                        Connections.delete_file(fl_id['datapath'])
                    server_tb=models.ServerDetails.objects.filter(user_id=userid).values()
                    for sr_id in server_tb:
                        qr_list=models.QuerySets.objects.filter(server_id=sr_id['id']).values()
                        for qr_id in qr_list:
                            query_set_id=qr_id['queryset_id']
                            Connections.delete_data(query_set_id,sr_id['id'],tok1['user_id'])
                        models.ServerDetails.objects.get(id=sr_id['id']).delete()
                    return Response({'message':'Deleted successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Not allowed to delete user'},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({'message':'User not exists'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)


class edit_roles(CreateAPIView):
    serializer_class=serializers.user_edit_role

    @transaction.atomic
    def put(self,request,rl_id,token):
        role_list=get_previlage_id(previlage=[previlages.edit_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                role_name=serializer.validated_data['role']
                previlage_list=serializer.validated_data['previlage_list']
                rl_data=role_create_status(role_name,previlage_list)
                if rl_data==200:
                    pass
                else:
                    return rl_data
                if models.Role.objects.filter(created_by=tok1['user_id'],role_id=rl_id).exists():
                    rldata=models.Role.objects.get(created_by=tok1['user_id'],role_id=rl_id)
                    if rldata.role==role_name:
                        role_name=rldata.role
                    else:
                        if models.Role.objects.filter(role__exact=role_name,created_by=tok1['user_id']).exists():
                            return Response({'message':'Role already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            role_name=rldata.role
                    models.Role.objects.filter(created_by=tok1['user_id'],role_id=rl_id).update(previlage_id=previlage_list,role=role_name,updated_at=updated_at)
                    models.Role.objects.filter(role_id=rl_id).update(updated_at=updated_at)
                    urtb=models.UserRole.objects.filter(role_id=rl_id).values()
                    for us in urtb:
                        AccessToken.objects.filter(user_id=us['user_id']).delete()
                    return Response({'message':'updated successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Role not exists for this user'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':'serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        

class edit_users(CreateAPIView):
    serializer_class=serializers.adding_user_serializer

    @transaction.atomic
    def put(self,request,us_id,token):
        role_list=get_previlage_id(previlage=[previlages.edit_roles,previlages.edit_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                firstname = serializer.validated_data['firstname']
                lastname = serializer.validated_data['lastname']
                username = serializer.validated_data['username']
                email = serializer.validated_data['email']
                active = serializer.validated_data['is_active']
                role = serializer.validated_data['role']
                password=12345
                conformpassword=12345
                if models.UserProfile.objects.filter(id=us_id).exists():
                    us_tb=user_status(firstname,lastname,username,email,password,conformpassword,role)
                    user_tb=models.UserProfile.objects.get(id=us_id)
                    for rl in role:
                        if models.Role.objects.filter(role=rl,created_by=tok1['user_id']).exists():
                            pass
                        else:
                            return Response({'message':'{} role not allowed to assign'.format(rl)},status=status.HTTP_406_NOT_ACCEPTABLE)
                    # usrole=models.UserRole.objects.filter(user_id=us_id).values()
                    # for rl_id in usrole:
                    #     if models.Role.objects.filter(role_id=rl_id['role_id'],created_by=tok1['user_id']).exists():
                    #         pass
                    #     else:
                    #         return Response({'message':'{} user not allowed to edit'.format(user_tb.username)},status=status.HTTP_406_NOT_ACCEPTABLE)
                    if models.UserProfile.objects.filter(email__iexact=email,id=us_id).exists():
                        pass
                    elif models.UserProfile.objects.filter(email__iexact=email).exists():
                        return Response({'message':'email already exists'},status=status.HTTP_404_NOT_FOUND)
                    elif models.UserProfile.objects.filter(username=username).exists():
                        return Response({'message':'username already exists'},status=status.HTTP_404_NOT_FOUND)
                    elif us_tb==200:
                        pass
                    else:
                        return us_tb
                    models.UserProfile.objects.filter(id=us_id).update(first_name=firstname,last_name=lastname,updated_at=updated_at,email=email,username=username,name=username,
                                                                       is_active=active)
                    models.UserRole.objects.filter(user_id=us_id).delete()
                    if role==[] or role=='':
                        rltd=models.UserRole.objects.create(user_id=us_id,created_by=tok1['user_id'],created_at=created_at,updated_at=updated_at)
                        models.UserRole.objects.filter(id=rltd.id).update(updated_at=updated_at,created_at=created_at)
                    else:
                        for rl in role:
                            rltb=models.Role.objects.get(role=rl,created_by=tok1['user_id'])
                            rltd=models.UserRole.objects.create(role_id=rltb.role_id,user_id=us_id,created_at=created_at,updated_at=updated_at,created_by=tok1['user_id'])
                            models.UserRole.objects.filter(id=rltd.id).update(updated_at=updated_at,created_at=created_at)
                    us_updated=models.UserProfile.objects.get(id=us_id)
                    try:
                        context = {'username':us_updated.username,'admin':tok1['username']}
                        html_message = render_to_string('role_update.html', context)
                        message = 'Roles Updated successfully'
                        subject = message
                        from_email = settings.EMAIL_HOST_USER
                        to_email = [us_updated.email.lower()]
                        send_mail(subject, message, from_email, to_email, html_message=html_message)
                    except:
                        return Response({'message':'SMTP Error'},status=status.HTTP_400_BAD_REQUEST)
                    return Response({'message':'Details updated successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'user not exists'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
        

@api_view(['GET'])
def role_details(request,rl_id,token):
    if request.method=='GET':
        role_list=get_previlage_id(previlage=[previlages.view_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            roles_list=models.Role.objects.get(role_id=rl_id)
            users_names=models.UserRole.objects.filter(role_id=roles_list.role_id).values()
            names=[]
            for i2 in users_names:
                ustb=models.UserProfile.objects.get(id=i2['user_id'])
                names.append(ustb.username)
            pr_list=[]
            for i3 in ast.literal_eval(roles_list.previlage_id):
                prev_name=models.previlages.objects.get(id=i3)
                data = {
                    "id":prev_name.id,
                    "previlage":prev_name.previlage
                }
                pr_list.append(data)
            return Response({'role_name':roles_list.role,'previlages':pr_list,'users':names},status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_406_NOT_ACCEPTABLE)
    


@api_view(['GET'])
def user_details(request,us_id,token):
    if request.method=='GET':
        role_list=get_previlage_id(previlage=[previlages.view_roles,previlages.view_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            try:
                us_data=models.UserProfile.objects.get(id=us_id)
            except:
                return Response({'message':'Uer_id not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
            userrole=models.UserRole.objects.filter(user_id=us_id,created_by=tok1['user_id']).values()
            role_nm=[]
            try:
                for rl in userrole:
                    rltb=models.Role.objects.get(role_id=rl['role_id'])
                    role_nm.append(rltb.role)
            except:
                role_nm=[]
            roles_us=models.Role.objects.filter(created_by=tok1['user_id']).values('role')
            user_roles=[usrl['role'] for usrl in roles_us]
            data = {
                    "user_id":us_data.id,
                    "name":us_data.name,
                    "username":us_data.username,
                    "firstname":us_data.first_name,
                    "lastname":us_data.last_name,
                    "email":us_data.email,
                    "is_active":us_data.is_active,
                    "created_by":tok1['username'],
                    "created_at":us_data.created_at.date(),
                    "updated_at":us_data.updated_at.date(),
                    "selected_roles":role_nm,
                    # "role":role_nm,
                    "existing_roles":user_roles
                }
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_406_NOT_ACCEPTABLE)




@api_view(['DELETE'])
def delete_role(request,roleid,token):
    if request.method=='DELETE':
        role_list=get_previlage_id(previlage=[previlages.delete_roles])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            if models.Role.objects.filter(role_id=roleid).exists():
                models.UserRole.objects.filter(role_id=roleid).update(role_id=None)
                models.Role.objects.filter(role_id=roleid).delete()
                return Response({'message':'Deleted successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Role not exists'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['GET'])
def user_roles_list_vi_dsbrd(request,token):
    if request.method=='GET':
        role_list=get_previlage_id(previlage=[previlages.view_roles,previlages.view_previlages,previlages.view_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            rolelist=[]
            prevg=models.previlages.objects.get(previlage='can view dashboard')
            roles_list=models.Role.objects.filter(created_by=tok1['user_id'],previlage_id__contains=prevg.id).values('role','role_id').order_by('-updated_at')
            for rl in roles_list:
                rolelist.append({'id':rl['role_id'],'role':rl['role']})
            return Response(rolelist,status=status.HTTP_200_OK)
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)


class roles_list_multiple(CreateAPIView):
    serializer_class=serializers.roles_list_seri

    @transaction.atomic
    def post(self,request,token):
        role_list=get_previlage_id(previlage=[previlages.view_roles,previlages.view_previlages,previlages.view_user])
        tok1 = role_status(token,role_list)
        if tok1['status']==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                role_ids=serializer.validated_data['role_ids']
                # final_data=[]
                names=[]
                for rl_id in role_ids:
                    if models.Role.objects.filter(role_id=rl_id,created_by=tok1['user_id']).exists():
                        pass
                    else:
                        return Response({'message':'Role{} not created by this user'.format(rl_id)},status=status.HTTP_406_NOT_ACCEPTABLE)
                    users_names=models.UserRole.objects.filter(role_id=rl_id,created_by=tok1['user_id']).values()
                    for i2 in users_names:
                        ustb=models.UserProfile.objects.get(id=i2['user_id'])
                        names.append({'user_id':ustb.id,'username':ustb.username})
                        # final_data.append(names)
                # role_list1234=[item for sublist in final_data for item in sublist]
                return Response(names,status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer value error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])