from rest_framework import serializers


class token_serializer(serializers.Serializer):
    redirect_url = serializers.CharField()
    # display_name = serializers.CharField()
    # token = serializers.CharField()

class display_name(serializers.Serializer):
    # display_name = serializers.CharField()
    redirect_url = serializers.CharField()
    # token = serializers.CharField()

class filter_date(serializers.Serializer):
    from_date = serializers.DateField(allow_null=True,default='')
    to_date = serializers.DateField(allow_null=True,default='')

class query_serializer(serializers.Serializer):
    table_name=serializers.CharField()
    database_id=serializers.IntegerField()

class connectwise_serializer(serializers.Serializer):
    company_id=serializers.CharField(default='',allow_null=True,allow_blank=True)
    site_url=serializers.CharField(default='',allow_null=True,allow_blank=True)
    public_key=serializers.CharField(default='',allow_null=True,allow_blank=True)
    private_key=serializers.CharField(default='',allow_null=True,allow_blank=True)
    client_id=serializers.CharField(default='',allow_null=True,allow_blank=True)
    display_name=serializers.CharField(default='',allow_null=True,allow_blank=True)
    hierarchy_id=serializers.IntegerField(default=None)


class halops_serializer(serializers.Serializer):
    site_url=serializers.CharField(default='',allow_null=True,allow_blank=True)
    client_id=serializers.CharField(default='',allow_null=True,allow_blank=True)
    client_secret=serializers.CharField(default='',allow_null=True,allow_blank=True)
    display_name=serializers.CharField(default='',allow_null=True,allow_blank=True)
    hierarchy_id=serializers.IntegerField(default=None)