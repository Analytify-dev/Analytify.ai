from django.db import models
import datetime
from dashboard import models as dash_models
from django.utils import timezone
from datetime import timedelta
# Create your models here.

def get_expiry_date():
    return timezone.now() + timedelta(minutes=60)

# token_expiry_time =datetime.datetime.now()+datetime.timedelta(minutes=60)

class TokenStoring(dash_models.TimeStampedModel):
    user = models.IntegerField(db_column='user_id',null=True,blank=True)
    parameter = models.CharField(max_length=100,null=True,blank=True)
    qbuserid = models.CharField(max_length=1000,db_column='quickbooks_user_id',null=True,blank=True)
    salesuserid = models.CharField(max_length=1000,db_column='salesforce_user_id',null=True,blank=True)
    tokentype = models.CharField(max_length=100,db_column='token_type',null=True,blank=True)
    accesstoken = models.CharField(max_length=1800,db_column='access_token',null=True,blank=True)
    refreshtoken = models.CharField(max_length=1800,db_column='refresh_token',null=True,blank=True)
    idtoken = models.CharField(max_length=1800,db_column='id_token',null=True,blank=True)
    realm_id = models.CharField(max_length=100,db_column='realm_id',null=True,blank=True)
    display_name = models.CharField(max_length=1000,db_column='display_name',null=True,blank=True)
    token_code = models.TextField(null=True,blank=True)
    domain_url = models.TextField(null=True,blank=True)
    # created_at = models.DateTimeField(default=datetime.datetime.now())
    # updated_at = models.DateTimeField(default=datetime.datetime.now())
    expiry_date = models.DateTimeField(default=get_expiry_date)

    class Meta:
        db_table = 'access_tokens'


class connectwise(dash_models.TimeStampedModel):
    user_id = models.IntegerField()
    company_id = models.TextField(null=True,blank=True)
    site_url = models.TextField(null=True,blank=True)
    public_key = models.TextField(null=True,blank=True)
    private_key = models.TextField(null=True,blank=True)
    client_id = models.TextField(null=True,blank=True)
    display_name = models.CharField(max_length=1000,null=True,blank=True)

    class Meta:
        db_table = 'connectwise'


class HaloPs(dash_models.TimeStampedModel):
    user_id = models.IntegerField()
    site_url = models.TextField(null=True,blank=True)
    client_id = models.TextField(null=True,blank=True)
    client_secret = models.TextField(null=True,blank=True)
    access_token = models.TextField(null=True,blank=True)
    display_name = models.CharField(max_length=1000,null=True,blank=True)
    expiry_date = models.DateTimeField(default=get_expiry_date)

    class Meta:
        db_table = 'HaloPs'