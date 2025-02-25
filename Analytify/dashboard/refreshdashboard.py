from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from dashboard.views import test_token
from dashboard import serializers    
from .dashboard_filter_apis import *
from .Filters import literal_eval
from quickbooks.reload import data_re_injecting

class RefrshedDashboardData(CreateAPIView):
    serializer_class = serializers.Drill_through_action_list

    @transaction.atomic()
    def put(self, request, token=None):
        if token==None:
            tok_status=200
        else:
            tok1 = test_token(token)
            tok_status=tok1['status']
        if tok_status != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({'message': 'serializer error'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        dashboard_id = serializer.validated_data["dashboard_id"]
        user_id = tok1['user_id']

        try:
            dashboarddata=dashboard_data.objects.get(id=dashboard_id)
        except:
            return Response({"message": "Invalid Dashboard ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if dashboarddata.is_public and token is None:
            return Response({"message": "Token is required for private dashboards"}, status=status.HTTP_401_UNAUTHORIZED)
        
        from dashboard import Connections
        hierarchy_ids = set(literal_eval(dashboarddata.hierarchy_id))

        for hierarchy_id in hierarchy_ids:

            ser_dt,para=Connections.display_name(hierarchy_id)
            tok1={'user_id':user_id}
            data_injecting=data_re_injecting(ser_dt,para,tok1)

            if not data_injecting==200:
                return data_injecting

        sheet_ids = eval(dashboarddata.sheet_ids) if isinstance(dashboarddata.sheet_ids, str) else dashboarddata.sheet_ids
        refreshed_data = []
        for sheet_id in sheet_ids:
            try:
                # Retrieve the sheet_data object
                sheet = sheet_data.objects.get(id=sheet_id)

                # Retrieve the associated query/queries from SheetFilter_querysets
                sheet_filters = SheetFilter_querysets.objects.get(Sheetqueryset_id=sheet.sheet_filt_id)

                if not sheet_filters:
                    return Response(
                        {"message": "No SheetFilter_querysets found for the given queryset_id."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # # Handle multiple filters (use the first one or loop through all)
                custom_query = sheet_filters.custom_query

                # Retrieve hierarchy_id from sheet_data
                hierarchy_id = sheet.hierarchy_id

                # Retrieve connection data using connection_data_retrieve
                connection_data = connection_data_retrieve(hierarchy_id, sheet.user_id)

                # Check if the connection is valid
                if connection_data.get("status") != 200:
                    return Response(
                        {"message": connection_data.get("message", "Unknown error")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Extract cursor and engine from the connection data
                cursor = connection_data.get("cursor")
                engine = connection_data.get("engine")


                colu = cursor.execute(text(custom_query))
                col_list = [column.replace(":OK",'') for column in colu.keys()]
                col_data = []
                for row in colu.fetchall():
                    col_data.append(list(row))

                a11 = []
                rows11=[]
                kk=ast.literal_eval(sheet_filters.columns)
                
                for i in kk:
                    result = {'column':[],'result':[]}
                    a = i.strip(' ')
                    a = a.replace('"',"")
                    if a in col_list:
                        ind = col_list.index(a)
                        result['column'] = col_list[ind]
                        result['result'] = [item[ind] for item in col_data] 
                    else:
                        result['column'] = a
                        result['result'] = []
                    a11.append(result)

                for i in ast.literal_eval(sheet_filters.rows):
                    result1 = {'column':[],'result':[]}
                    a = i.strip(' ')
                    a =a.replace('"',"") 
                    if a in col_list:
                        ind = col_list.index(a)
                        result1['column'] = col_list[ind]
                        result1['result'] = [item[ind] for item in col_data]
                    else:
                        result1['column'] = a
                        result1['result'] = []
                    rows11.append(result1)

                refreshed_data.append({
                        "sheet_id": sheet_id,
                        "Sheetqueryset_id": sheet_id,
                        "columns": a11,
                        "rows": rows11,
                        "queryset_id": sheet.queryset_id,
                        "chart_id": sheet_data.objects.get(id = sheet_id).chart_id,
                        "databaseId":QuerySets.objects.get(queryset_id = sheet.queryset_id,user_id=user_id).hierarchy_id
                    })

                if not refreshed_data:
                    return Response(
                        {"message": "No valid queries were found or executed."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            except sheet_data.DoesNotExist:
                return Response({"message": "Sheet data not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(refreshed_data, status=status.HTTP_200_OK)
