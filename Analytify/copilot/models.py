from django.db import models
from dashboard.models import UserProfile

# Create your models here.
class GPTAPIKey(models.Model):
    api_key = models.CharField(max_length=255)
    api_key_status = models.BooleanField(default=False)  # Assuming True means active, False means inactive
    gpt_model = models.CharField(max_length=100,default='gpt-3.5-turbo-0125',null=True)
    added_by = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gpt_api_key'