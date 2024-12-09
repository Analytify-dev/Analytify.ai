import requests
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import datetime
from django.db import transaction
import re, random
from pytz import utc
from dashboard.models import UserProfile,Account_Activation,UserConfigurations
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from oauth2_provider.models import AccessToken,Application,RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
# from django.conf import settings
from project import settings
from django.utils.crypto import get_random_string
from dashboard import serializers, models, views
from django.contrib.auth.hashers import make_password,check_password
from oauth2_provider.views.generic import ProtectedResourceView
# from dashboard.views import test_token
import psycopg2,sqlite3
import secrets
import string
import ast
import threading
from django.core.management import call_command
import os ,io
from django.core.files.uploadedfile import InMemoryUploadedFile



def signup_thread(user_id):
    
    try:
        BASE_DIR = settings.BASE_DIR
        # Construct the full path to the file
        file_path = os.path.join(BASE_DIR, 'insightapps-sample')
        
        # Load the file content
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Create an InMemoryUploadedFile instance
        file_obj = InMemoryUploadedFile(
            file=io.BytesIO(file_content),  # File content wrapped in BytesIO
            field_name='database_path',
            name='insightapps-sample',
            content_type='application/x-sqlite3',
            size=len(file_content),
            charset=None
        )
        
        server_details_instance =models.ServerDetails.objects.create(
            server_type = 4,
            user_id = user_id,
            is_sample = True,
            database_path = file_obj,
            display_name = 'example',
            is_connected = True,
            created_at = datetime.datetime.now(),
            updated_at = datetime.datetime.now()
        )
        server_details_instance.save()
        server_id = server_details_instance.id
    except Exception as e:
        return Response({'message':str(e)})
    # Call the import_data command with the user_id
    try:
        call_command('sample_dashboard', user_id , server_id)
    except Exception as e:
        pass

    try:
        # call_command('sample_dashboard2', adtb.id)
        call_command('sample_dashboard3', user_id, server_id)
    except:
        pass
    
    try:
        call_command('sample_dashboard4', user_id, server_id)
    except:
        pass
    
    try:
        call_command('sample_dashboard5', user_id, server_id)
    except:
        pass
        # return Response({"message":str(e)},status=status.HTTP_406_NOT_ACCEPTABLE)

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now()+datetime.timedelta(days=2)

class MyProtectedView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Protected resource accessed'})


def application():
    client_secret = get_random_string(length=32)
    application = Application.objects.create(
        name='InsightApps',
        # user=user,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        redirect_uris='http://127.0.0.1:8000/callback/',
        client_secret=client_secret,
    )
    en_str=views.encode_string(client_secret)
    Application.objects.filter(client_id=application.client_id).update(post_logout_redirect_uris=en_str)
    data = {
        'client_id':application.client_id,
        'client_secret':client_secret,
        'redirect_url':application.redirect_uris
    }
    return data

try:
    if Application.objects.filter(id=1).exists():
        ap_oauth=Application.objects.get(id=1)
        en_str=views.decode_string(ap_oauth.post_logout_redirect_uris)
        o_client_secret=en_str
        o_client_id=ap_oauth.client_id
        o_redirect=ap_oauth.redirect_uris
    else:
        ap_oauth=application()
        o_client_id = ap_oauth['client_id']
        o_client_secret = ap_oauth['client_secret']
        o_redirect = ap_oauth['redirect_url']


    CLIENT_ID = o_client_id
    CLIENT_SECRET = o_client_secret
    TOKEN_URL = settings.TOKEN_URL
    O_REDIRECT_URI = o_redirect
except:
    pass

def get_access_token(username, password):
    token_url = TOKEN_URL
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret,
        'user':username
    }
    response = requests.post(token_url, data=data)
    if response.status_code==200:
        data = {
            'status':200,
            'data':response.json()
        }
    else:
        data = {
            'status':response.status_code,
            'data':response
        }
    return data


def license_key(email,u_id,max_limit):
    try:
        password = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(300)))
        models.license_key.objects.filter(user_id=u_id).delete()
        context = {'license_key': password,'max_limit':max_limit}
        html_message = render_to_string('license.html', context)
        message = 'Hello, welcome to our website!'
        subject = "Welcome to InsightApps: License key to connect"
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        send_mail(subject, message, from_email, to_email, html_message=html_message)
        models.license_key.objects.create(user_id=u_id,max_limit=max_limit,key=password,created_at=created_at,
                                        updated_at=updated_at)#,expired_at=datetime.datetime.now()+datetime.timedelta(days=24)
        return Response({'message':'License key sent to mail successfully, Please activate the License Key'},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message':'SMTP Error'},status=status.HTTP_400_BAD_REQUEST)



###########  Sign_up   ################

class signupView(CreateAPIView):
    serializer_class= serializers.register_serializer

    @transaction.atomic()
    @csrf_exempt
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            u=serializer.validated_data['username']
            email = serializer.validated_data['email']
            pwd=serializer.validated_data['password']
            cnfpwd=serializer.validated_data['conformpassword']
            if (models.UserProfile.objects.filter(username=u).exists()):
                return Response({"message": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif len(u)>30:
                return Response({"message": "usernme allows upto 30 characters only"}, status=status.HTTP_400_BAD_REQUEST)
            elif (models.UserProfile.objects.filter(email__iexact=email).exists()):
                return Response({"message": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"

            r= re.findall(pattern,pwd)
            if not r:
                return Response({"message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."},status=status.HTTP_406_NOT_ACCEPTABLE)
            if pwd!=cnfpwd:
                return Response({"message":"Password did not matched"},status=status.HTTP_406_NOT_ACCEPTABLE)

            try:
                unique_id = get_random_string(length=64)
                # protocol ='https://'
                # current_site = 'hask.io/'
                current_site = str(settings.link_url)
                api = 'authentication/activate_account/'
                Gotp = random.randint(10000,99999)
                context = {'Gotp': Gotp,'api':api,'unique_id':unique_id,'current_site':current_site}
                html_message = render_to_string('registration_email.html', context)
        
                message = 'Hello, welcome to our website!'
                subject = "Welcome to InsightApps: Verify your account"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email.lower()]
                send_mail(subject, message, from_email, to_email, html_message=html_message)
                adtb=models.UserProfile.objects.create_user(username=u,name=u,password=pwd,email=email,is_active=False,created_at=created_at,updated_at=updated_at)
                models.Account_Activation.objects.create(user = adtb.id, key = unique_id, otp=Gotp,email=email,created_at=created_at,expiry_date=expired_at)
            except:
                return Response({"message":f"SMTP Error"},status=status.HTTP_400_BAD_REQUEST)
                
            try:
                rlmd=models.Role.objects.get(role='Admin')
            except:
                prev=models.previlages.objects.all().values()
                pr_ids=[i1['id'] for i1 in prev]
                rlmd=models.Role.objects.create(role='Admin',role_desc="All previlages",previlage_id=pr_ids)
            models.UserRole.objects.create(role_id=rlmd.role_id,user_id=adtb.id)
            user_id=adtb.id
            thread = threading.Thread(target=signup_thread, args=(user_id,))
            thread.start()
            data = {
                "message" : "Account Activation Email Sent",
                "email" : email.lower(),
                "emailActivationToken"  : unique_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Serializer Value Error"},status=status.HTTP_400_BAD_REQUEST)  


class AccountActivateView(CreateAPIView):
    serializer_class = serializers.activation_serializer

    @csrf_exempt
    @transaction.atomic
    def post(self,request,token):
        try:
            token = models.Account_Activation.objects.get(key=token)
        except:
            return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)
        if token.expiry_date > datetime.datetime.now(utc):
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                u_id = token.user
                otp_valid = token.otp
                otp = serializer.validated_data['otp']
                if otp=='' or otp==None or len(str(otp)) < 5:
                    return Response({'message':'OTP field cannot be empty'},status=status.HTTP_406_NOT_ACCEPTABLE)
                if otp_valid ==otp:
                    models.UserProfile.objects.filter(id=u_id).update(is_active='True')
                    models.Account_Activation.objects.filter(user = u_id).delete()
                    # license1=license_key(token.email.lower(),u_id,max_limit=settings.db_connections)
                    return Response({"message" : "Account successfully activated"},status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message":"Enter OTP"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Activation Token/ OTP Expired"} , status=status.HTTP_401_UNAUTHORIZED)  
        

class LoginApiView(CreateAPIView):
    serializer_class = serializers.login_serializer

    @csrf_exempt
    def post(self,request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email  = serializer.data['email']
            password = serializer.data['password']
            if (models.UserProfile.objects.filter(email__iexact=email).exists()):
                if (models.UserProfile.objects.filter(email__iexact=email,is_active=True).exists()):
                    data = models.UserProfile.objects.get(email__iexact=email)
                    try:
                        user = authenticate(username=data, password=password)
                    except:
                        return Response({"message":"Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED) 
                    AccessToken.objects.filter(expires__lte=datetime.datetime.now(utc)).delete()
                    if user is not None:
                        access_token=get_access_token(data,password)
                        if access_token['status']==200:
                            # AccessToken.objects.filter(token=access_token['data']['access_token']).update(is_allowed=False)
                            userrole=models.UserRole.objects.filter(user_id=data.id).values()
                            prev_name_li=[]
                            roles=[]
                            for i1 in userrole:
                                if i1['role_id']==None or i1['role_id']=='':
                                    prev_name_li=prev_name_li
                                else:
                                    roles_list=models.Role.objects.get(role_id=i1['role_id'])
                                    roles.append(roles_list.role)
                                    for i3 in ast.literal_eval(roles_list.previlage_id):
                                        prev_name=models.previlages.objects.get(id=i3)
                                        prev_name_li.append({"id":prev_name.id,
                                            "previlage":prev_name.previlage})
                            login(request, user)
                            views.reassign_user_sample_dashboard(data.id)
                            if UserConfigurations.objects.filter(user_id=data.id).exists():
                                                                
                                chart_type=UserConfigurations.objects.get(user_id=data.id).chart_type
                            else:
                                UserConfigurations.objects.update_or_create(
                                                    user_id=data.id, 
                                                    defaults={"chart_type": "echart"})
                                chart_type="echart"
                            data = ({
                                "accessToken":access_token['data']['access_token'],
                                "username":data.username,
                                "email":data.email,
                                "first_name":data.first_name,
                                "last_name":data.last_name,
                                "user_id":data.id,
                                "is_demo_account":data.demo_account,
                                "is_active":data.is_active,
                                "created_at":data.created_at,
                                "roles":roles,
                                "previlages":prev_name_li,
                                "chart_type":chart_type
                            })
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            return Response(access_token,status=access_token['status'])
                    else:
                        return Response({"message" : "Incorrect password"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message":'Account is in In-Active, please Activate your account'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"message" :"You do not have an account, Please SIGNUP with InsightApps"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message" : "Enter Email and Password"}, status=status.HTTP_400_BAD_REQUEST)



class Account_reactivate(CreateAPIView):
    serializer_class = serializers.ForgetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            if UserProfile.objects.filter(email__iexact=email,is_active=True).exists():
                return Response({"message":"Account already Activated, please login"},status=status.HTTP_408_REQUEST_TIMEOUT)
            elif UserProfile.objects.filter(email__iexact=email).exists():
                pass
            else:
                return Response({"message":"You do not have an account, Please SIGNUP with InsightApps"},status=status.HTTP_404_NOT_FOUND)
            name = UserProfile.objects.get(email__iexact=email)
            try:
                unique_id = get_random_string(length=64)
                # protocol ='https://'
                # current_site = 'hask.io/'
                current_site = str(settings.link_url)
                api = 'authentication/activate_account/'
                Gotp = random.randint(10000,99999)
                context = {'Gotp': Gotp,'api':api,'unique_id':unique_id,'current_site':current_site}
                html_message = render_to_string('account_reactivate.html', context)
        
                message = 'Hello, welcome to InsightApps website!'
                subject = "Welcome to InsightApps: Verify your account"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email.lower()]
                send_mail(subject, message, from_email, to_email, html_message=html_message)

                Account_Activation.objects.create(user = name.id, key = unique_id,otp=Gotp,email=email,created_at=created_at,expiry_date=expired_at)
                data = {
                    "message" : "Account Activation Email Sent",
                    "email" : email.lower(),
                    "emailActivationToken"  : unique_id
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except :
                return Response({"message":"SMTP Error"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response ({"message":"Serializer Value Error"}, status=status.HTTP_400_BAD_REQUEST)
        


class ForgotPasswordView(CreateAPIView):
    serializer_class = serializers.ForgetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            if UserProfile.objects.filter(email__iexact=email).exists():
                pass
            else:
                return Response({"message":"You do not have an account, Please SIGNUP with InsightApps"},status=status.HTTP_404_NOT_FOUND)
            name = UserProfile.objects.get(email__iexact=email)
            u_id = name.id
            models.Reset_Password.objects.filter(user=u_id).delete()
            try:
                unique_id = get_random_string(length=32)
                # current_site = 'hask.io/'
                # protocol ='https://'
                current_site = str(settings.link_url)
                # interface = get_user_agent(request)
                models.Reset_Password.objects.create(user=u_id, key=unique_id,created_at=created_at)
                subject = "InsightApps Reset Password Assistance"
                api = 'authentication/reset-password/'
                context = {'username':name.username,'api':api,'unique_id':unique_id,'current_site':current_site}
                html_message = render_to_string('reset_password.html', context)

                send_mail(
                    subject = subject,
                    message = "Hi {}, \n\nThere was a request to change your password! \n\nIf you did not make this request then please ignore this email. \n\nYour password reset link \n {}{}{}".format(name.username,current_site, api, unique_id),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )
                data = {
                    "message" : "Password reset email sent",
                    "Passwordresettoken" : unique_id
                }
                return Response(data,status=status.HTTP_200_OK)
            except:
                return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response ({"message":"Serializer Value Error"}, status=status.HTTP_400_BAD_REQUEST)
        


class ConfirmPasswordView(CreateAPIView):
    serializer_class = serializers.ConfirmPasswordSerializer

    def put(self, request, token):
        try:
            token = models.Reset_Password.objects.get(key=token)
        except:
            return Response({"message":"Token Doesn't Exists"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            name = token.user
            use = UserProfile.objects.get(id=name)
            email = use.email
            pwd=serializer.validated_data['password']
            cnfpwd=serializer.validated_data['confirmPassword']
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"
            r= re.findall(pattern,pwd)
            if not r:
                data={
                    "message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."
                }
                return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
            elif pwd!=cnfpwd:
                return Response({"message":"Passsword did not matched"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                pass

            try:
                date_string = datetime.datetime.now().date()
                date_obj = datetime.datetime.strptime(str(date_string), '%Y-%m-%d')
                date = date_obj.strftime('%d %b %Y').upper()
                time_string = datetime.datetime.now().time()  # Current time Format 12:34:46.9875
                time = str(time_string).split('.')[0] # Converted Time 12:34:46
                context = {'username':use.username,"date":date,"time":time}
                html_message = render_to_string('reset_password_success.html', context)
                subject = "Password change alert Acknowledgement"
                send_mail(
                    subject = subject,
                    message = "Hi {}, \nYou have successfully changed your InsightApps Login password on {} at {} . Do not share with anyone..\nDo not disclose any confidential information such as Username, Password, OTP etc. to anyone.\n\nBest regards,\nThe InsightApps Team".format(use.username,date,time),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )
                UserProfile.objects.filter(id=name).update(password=make_password(pwd),updated_at=datetime.datetime.now())
                models.Reset_Password.objects.filter(user=use.id).delete()
                return Response({"message" : "Password changed Successfully, Please Login"}, status=status.HTTP_200_OK)
            except:
                return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message":"Password Fields didn't Match"}, status=status.HTTP_400_BAD_REQUEST)
        


# Update/Change Password 
class UpdatePasswordAPI(CreateAPIView):
    serializer_class = serializers.UpdatePasswordSerializer

    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            usertable=UserProfile.objects.get(id=tok1['user_id'])
            serializer = self.get_serializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                current_pwd = serializer.validated_data['current_password']
                new_pwd = serializer.validated_data['new_password']
                confirm_pwd = serializer.validated_data['confirm_password']
                pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"
                r=re.findall(pattern,new_pwd)
                if check_password(current_pwd, usertable.password):
                    pass
                else:
                    return Response({"message":"Incorrect Current Password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                if not r:
                    data={
                        "message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."
                    }
                    return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
                elif len(new_pwd)<8 or len(confirm_pwd)<8:
                    return Response({"message":"Check Password Length"}, status=status.HTTP_400_BAD_REQUEST)
                elif new_pwd!=confirm_pwd:
                    return Response({"message":"Password did not matched"},status=status.HTTP_406_NOT_ACCEPTABLE)
                if new_pwd==confirm_pwd:
                    UserProfile.objects.filter(id=usertable.id).update(password=make_password(new_pwd),updated_at=datetime.datetime.now())
                    return Response({"message":"Password Updated Successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"There was an error with your Password combination"}, status=status.HTTP_406_NOT_ACCEPTABLE)                        
            else:
                return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])


class UpdateEMAILAPI(CreateAPIView):
    serializer_class = serializers.ForgetPasswordSerializer

    @transaction.atomic
    def post(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer = self.get_serializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data['email']
                if UserProfile.objects.filter(email__iexact=email).exists():
                    return Response({"message":"Email already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    pass
                try:
                    Account_Activation.objects.filter(email__iexact=email).delete()
                    unique_id = get_random_string(length=64)
                    # protocol ='https://'
                    # current_site = 'hask.io/'
                    current_site = str(settings.link_url)
                    api = 'core/activate_account/'

                    Gotp = random.randint(10000,99999)
                    message = "Hi {},\n\n Request For Email Update.\nYour One-Time Password is {}\nTo Change your Email, please click on the following url:\n {}{}{}\n".format(tok1['username'],Gotp,current_site,api,unique_id)
                    subject = "InsightApps Email Update Request"
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [email]
                    send_mail(subject, message, from_email, to_email)
                    Account_Activation.objects.create(user=tok1['user_id'], key = unique_id, otp=Gotp, email=email,created_at=created_at,expiry_date=expired_at)

                    data = {
                        "message" : "Requested for Email Update", 
                        "emailActivationToken": unique_id
                        }
                    return Response(data, status=status.HTTP_200_OK)
                except:
                    return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])

            
class CustomerEmailUpdateView(CreateAPIView):
    serializer_class = serializers.activation_serializer

    @transaction.atomic
    def put(self,request,ustoken,act_token):
        tok1 = views.test_token(ustoken)
        if tok1['status']==200:
            try:
                token=Account_Activation.objects.get(key=act_token)
            except:
                return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)
            if token.expiry_date >= token.created_at:
                serializer=self.get_serializer(data=request.data)
                if serializer.is_valid():
                    u_id = token.user
                    otp_valid = token.otp
                    otp = serializer.validated_data['otp']
                    if otp_valid==otp:
                        UserProfile.objects.filter(id=u_id).update(email=token.email,updated_at=datetime.datetime.now())
                        Account_Activation.objects.filter(user=u_id).delete()
                        return Response({"message" : "Email Updated Successfully"},status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({"message":"Enter OTP"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message" : "Activation Token/ OTP Expired"} , status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(tok1,status=tok1['status'])
        

class user_data_update(CreateAPIView):
    serializer_class=serializers.name_update_serializer

    @transaction.atomic
    def put(self,request,token):
        tok1 = views.test_token(token)
        if tok1['status']==200:
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                username = serializer.validated_data['username']
                # if username=='':
                #     uname=UserProfile.objects.get(id=tok1['user_id'])
                #     username=uname.name
                # else:
                #     username=username
                UserProfile.objects.filter(id=tok1['user_id']).update(name=username,updated_at=datetime.datetime.now())
                return Response({"message":"Updated successfully"},status=status.HTTP_200_OK)
            else:
                return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(tok1,status=tok1['status'])
        


class license_key_verify(CreateAPIView):
    serializer_class=serializers.license_serializer

    @csrf_exempt
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            key = serializer.validated_data['key']
            try:
                lic1=models.license_key.objects.get(key=key)
                models.license_key.objects.filter(user_id=lic1.user_id,key=key).update(is_validated=True)
                return Response({'message':'Validated Successfylly'},status=status.HTTP_200_OK)
            except:
                return Response({'message':'License key is not valid'},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)

        
        

class license_reactivation(CreateAPIView):
    serializer_class=serializers.ForgetPasswordSerializer

    @csrf_exempt
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            if UserProfile.objects.filter(email=email).exists():
                pass
            else:
                return Response({"message":"You do not have an account, Please SIGNUP with InsightApps"},status=status.HTTP_404_NOT_FOUND)
            name = UserProfile.objects.get(email=email)
            licen1=license_key(name.email.lower(),name.id,max_limit=10)
            return licen1
        else:
            return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
        

class otp_resend(CreateAPIView):
    serializer_class=serializers.otp_resend

    @csrf_exempt
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data['token']
            ac_tb=models.Account_Activation.objects.get(key=token)
            email=ac_tb.email
            try:
                current_site = str(settings.link_url)
                api = 'authentication/activate_account/'
                Gotp = random.randint(10000,99999)
                context = {'Gotp': Gotp,'api':api,'unique_id':ac_tb.key,'current_site':current_site}
                html_message = render_to_string('registration_email.html', context)
                message = 'Hello, welcome to our website!'
                subject = "Welcome to InsightApps: Verify your account"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email.lower()]
                
                send_mail(subject, message, from_email, to_email, html_message=html_message)
                models.Account_Activation.objects.filter(key=token).update(otp=Gotp)
                data = {
                    "message" : "Account Activation Email Sent",
                    "email" : email.lower(),
                    "emailActivationToken"  : ac_tb.key
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except:
                return Response({"message":f"SMTP Error"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
