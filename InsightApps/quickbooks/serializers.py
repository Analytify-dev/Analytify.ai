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
