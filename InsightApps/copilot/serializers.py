from rest_framework import serializers


class ChartCopilot(serializers.Serializer):
    id = serializers.IntegerField()
    prompt = serializers.CharField(default=None,allow_null=True)
    # prompt = serializers.CharField(default="Get Cateory Wise Profit")

class ChartDataRequestSerializer(serializers.Serializer):
    chart_index = serializers.IntegerField()
    queryset_id = serializers.IntegerField()

class APIKEYServerialzer(serializers.Serializer):
    key = serializers.CharField()