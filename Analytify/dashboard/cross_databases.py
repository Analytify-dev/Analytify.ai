
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from dashboard import models,serializers,views,roles,previlages,files,clickhouse,Connections
from sqlalchemy import text,inspect
from quickbooks import models as qb_models
from clickhouse_driver import Client
from project import settings
import clickhouse_connect
import re
from django.db import connection
from rest_framework.decorators import api_view


# client = Client(host=settings.clickhouse_host, database='default')

class user_db_tables(CreateAPIView):
    serializer_class=serializers.test_data

    def post(self,request,token):
        tok1 = views.test_token(token)
        if not tok1['status']==200:
            return Response(tok1,status=tok1['status'])
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            # Search Filter Only works on Display Name Column in Server Details
            search = serializer.validated_data['search']
            page_no = serializer.validated_data['page_no']
            page_count = serializer.validated_data['page_count']
            if search =='':
                details = models.ServerDetails.objects.filter(user_id=tok1['user_id'],is_connected=True).values().order_by('-updated_at')
                filedetai = models.FileDetails.objects.filter(user_id=tok1['user_id'],quickbooks_user_id=None).values().order_by('-updated_at')
                quickdetai = qb_models.TokenStoring.objects.filter(user=tok1['user_id']).values().order_by('-updated_at')
                connectdata = qb_models.connectwise.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
                halopsdata = qb_models.HaloPs.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
                shopifydata = qb_models.Shopify.objects.filter(user_id=tok1['user_id']).values().order_by('-updated_at')
            else:
                details = models.ServerDetails.objects.filter(user_id=tok1['user_id'],is_connected=True,display_name__icontains=search).values().order_by('-updated_at')
                filedetai = models.FileDetails.objects.filter(user_id=tok1['user_id'],display_name__icontains=search,quickbooks_user_id=None).values().order_by('-updated_at')
                quickdetai = qb_models.TokenStoring.objects.filter(user=tok1['user_id'],display_name__icontains=search).values().order_by('-updated_at')
                connectdata = qb_models.connectwise.objects.filter(user_id=tok1['user_id'],display_name__icontains=search).values().order_by('-updated_at')
                halopsdata = qb_models.HaloPs.objects.filter(user_id=tok1['user_id'],display_name__icontains=search).values().order_by('-updated_at')
                shopifydata = qb_models.Shopify.objects.filter(user_id=tok1['user_id'],display_name__icontains=search).values().order_by('-updated_at')
            Final_list=[]
            datasets=[details,filedetai,quickdetai,connectdata,halopsdata,shopifydata]
            paraeter=['server','files','quickbooks','connectwise','halops','shopify']
            for dataset,pamet in zip(datasets,paraeter):
                for data in dataset:
                    pr_id=models.parent_ids.objects.get(table_id=data['id'],parameter=pamet)
                    try:
                        clickhouse_class = clickhouse.Clickhouse(data['display_name'])
                        engine = clickhouse_class.engine
                        cursor = clickhouse_class.cursor
                    except:
                        return Response({'message': "Connection closed, Re-Connect"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    
                    inspector = inspect(engine)
                    schema_name = data['display_name']
                    
                    if schema_name != 'information_schema':
                        table_names = sorted(inspector.get_table_names(schema=schema_name))
                    else:
                        table_names = []
                    tables_list=[]
                    for table_name in table_names:
                        columns = inspector.get_columns(table_name, schema=schema_name)
                        cols = [{"column": column['name'], 
                                "datatype": str(column['type']).lower() if column['type'] is not None else 'unknown'} 
                                for column in columns]
                        tables_list.append({'table':table_name,'collumns':cols})                    
                    cursor.close()
                    Final_list.append({'hierarchy_id':pr_id.id,'database': schema_name, 'schema': schema_name, 'tables':tables_list})
            try:
                resul_data=Connections.pagination(request,Final_list,page_no,page_count)
                if not resul_data['status']==200:
                    return resul_data
                return Response(resul_data,status=status.HTTP_200_OK)
            except:
                return Response({'message':'Empty page/data not exists/selected count of records are not exists'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':"Serialzer Error"},status=status.HTTP_404_NOT_FOUND)





def run_union_all(*queries):
    """
    Dynamically aligns columns for UNION ALL in ClickHouse.
    - Keeps original columns.
    - Adds missing columns as NULL.
    - Removes double quotes for ClickHouse compatibility.
    - Executes a single UNION ALL query.
    """
    extracted_queries = []
    all_columns = set()
    query_column_map = []
    # Extract column names from each query
    for query in queries:
        # Extract column names using regex
        match = re.findall(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        # Extract column names while preserving AS aliases
        columns = [col.strip().rsplit(" AS ", 1)[-1] for col in match[0].split(",")]
        all_columns.update(columns)
        query_column_map.append((query, columns))
    all_columns = sorted(all_columns)  # Ensure consistent column order
    # Construct modified queries with NULL for missing columns
    for query, columns in query_column_map:
        select_parts = []
        for col in all_columns:
            if col in columns:
                select_parts.append(f"{col}")  # Keep original column
            else:
                select_parts.append(f"NULL AS {col}")  # Add missing column as NULL
        # Replace the original SELECT part with the modified one
        modified_query = re.sub(
            r'SELECT\s+(.*?)\s+FROM',
            f"SELECT {', '.join(select_parts)} FROM",
            query,
            flags=re.IGNORECASE | re.DOTALL
        )
        extracted_queries.append(modified_query)
    final_query = " UNION ALL ".join(extracted_queries)
    return final_query



@api_view(['GET'])
def query_test(request):
    q1 = "SELECT \"HaloPs\".\"id\" AS \"id\", \"HaloPs\".\"created_at\" AS \"created_at\", \"HaloPs\".\"updated_at\" AS \"updated_at\", \"HaloPs\".\"user_id\" AS \"user_id\", \"HaloPs\".\"site_url\" AS \"site_url\", \"HaloPs\".\"client_id\" AS \"client_id\", \"HaloPs\".\"client_secret\" AS \"client_secret\", \"HaloPs\".\"access_token\" AS \"access_token\", \"HaloPs\".\"display_name\" AS \"display_name\", \"HaloPs\".\"expiry_date\" AS \"expiry_date\" FROM \"insightapps_dev\".\"HaloPs\" AS \"HaloPs\" LIMIT 100"
    q2 = "SELECT \"company_companies\".\"id\" AS \"id\", \"company_companies\".\"identifier\" AS \"identifier\", \"company_companies\".\"name\" AS \"name\", \"company_companies\".\"status.id\" AS \"status.id\", \"company_companies\".\"status.name\" AS \"status.name\", \"company_companies\".\"status._info.status_href\" AS \"status._info.status_href\", \"company_companies\".\"country.id\" AS \"country.id\", \"company_companies\".\"country.name\" AS \"country.name\", \"company_companies\".\"country._info.country_href\" AS \"country._info.country_href\", \"company_companies\".\"phoneNumber\" AS \"phoneNumber\", \"company_companies\".\"website\" AS \"website\", \"company_companies\".\"territory.id\" AS \"territory.id\", \"company_companies\".\"territory.name\" AS \"territory.name\", \"company_companies\".\"territory._info.location_href\" AS \"territory._info.location_href\", \"company_companies\".\"market.id\" AS \"market.id\", \"company_companies\".\"market.name\" AS \"market.name\", \"company_companies\".\"market._info.Market_href\" AS \"market._info.Market_href\", \"company_companies\".\"defaultContact.id\" AS \"defaultContact.id\", \"company_companies\".\"defaultContact.name\" AS \"defaultContact.name\", \"company_companies\".\"defaultContact._info.contact_href\" AS \"defaultContact._info.contact_href\", \"company_companies\".\"dateAcquired\" AS \"dateAcquired\", \"company_companies\".\"annualRevenue\" AS \"annualRevenue\", \"company_companies\".\"timeZoneSetup.id\" AS \"timeZoneSetup.id\", \"company_companies\".\"timeZoneSetup.name\" AS \"timeZoneSetup.name\", \"company_companies\".\"timeZoneSetup._info.timeZoneSetup_href\" AS \"timeZoneSetup._info.timeZoneSetup_href\", \"company_companies\".\"leadFlag\" AS \"leadFlag\", \"company_companies\".\"unsubscribeFlag\" AS \"unsubscribeFlag\", \"company_companies\".\"taxCode.id\" AS \"taxCode.id\", \"company_companies\".\"taxCode.name\" AS \"taxCode.name\", \"company_companies\".\"taxCode._info.taxCode_href\" AS \"taxCode._info.taxCode_href\", \"company_companies\".\"billingTerms.id\" AS \"billingTerms.id\", \"company_companies\".\"billingTerms.name\" AS \"billingTerms.name\", \"company_companies\".\"billToCompany.id\" AS \"billToCompany.id\", \"company_companies\".\"billToCompany.identifier\" AS \"billToCompany.identifier\", \"company_companies\".\"billToCompany.name\" AS \"billToCompany.name\", \"company_companies\".\"billToCompany._info.company_href\" AS \"billToCompany._info.company_href\", \"company_companies\".\"invoiceDeliveryMethod.id\" AS \"invoiceDeliveryMethod.id\", \"company_companies\".\"invoiceDeliveryMethod.name\" AS \"invoiceDeliveryMethod.name\", \"company_companies\".\"deletedFlag\" AS \"deletedFlag\", \"company_companies\".\"mobileGuid\" AS \"mobileGuid\", \"company_companies\".\"isVendorFlag\" AS \"isVendorFlag\", \"company_companies\".\"types[0].id\" AS \"types[0].id\", \"company_companies\".\"types[0].name\" AS \"types[0].name\", \"company_companies\".\"types[0]._info.type_href\" AS \"types[0]._info.type_href\", \"company_companies\".\"site.id\" AS \"site.id\", \"company_companies\".\"site.name\" AS \"site.name\", \"company_companies\".\"site._info.site_href\" AS \"site._info.site_href\", \"company_companies\".\"_info.lastUpdated\" AS \"_info.lastUpdated\", \"company_companies\".\"_info.updatedBy\" AS \"_info.updatedBy\", \"company_companies\".\"_info.dateEntered\" AS \"_info.dateEntered\", \"company_companies\".\"_info.enteredBy\" AS \"_info.enteredBy\", \"company_companies\".\"_info.contacts_href\" AS \"_info.contacts_href\", \"company_companies\".\"_info.agreements_href\" AS \"_info.agreements_href\", \"company_companies\".\"_info.tickets_href\" AS \"_info.tickets_href\", \"company_companies\".\"_info.opportunities_href\" AS \"_info.opportunities_href\", \"company_companies\".\"_info.activities_href\" AS \"_info.activities_href\", \"company_companies\".\"_info.projects_href\" AS \"_info.projects_href\", \"company_companies\".\"_info.configurations_href\" AS \"_info.configurations_href\", \"company_companies\".\"_info.orders_href\" AS \"_info.orders_href\", \"company_companies\".\"_info.documents_href\" AS \"_info.documents_href\", \"company_companies\".\"_info.sites_href\" AS \"_info.sites_href\", \"company_companies\".\"_info.teams_href\" AS \"_info.teams_href\", \"company_companies\".\"_info.reports_href\" AS \"_info.reports_href\", \"company_companies\".\"_info.notes_href\" AS \"_info.notes_href\", \"company_companies\".\"addressLine1\" AS \"addressLine1\", \"company_companies\".\"addressLine2\" AS \"addressLine2\", \"company_companies\".\"city\" AS \"city\", \"company_companies\".\"state\" AS \"state\", \"company_companies\".\"zip\" AS \"zip\", \"company_companies\".\"faxNumber\" AS \"faxNumber\", \"company_companies\".\"accountNumber\" AS \"accountNumber\", \"company_companies\".\"numberOfEmployees\" AS \"numberOfEmployees\", \"company_companies\".\"leadSource\" AS \"leadSource\", \"company_companies\".\"billingContact.id\" AS \"billingContact.id\", \"company_companies\".\"billingContact.name\" AS \"billingContact.name\", \"company_companies\".\"billingContact._info.contact_href\" AS \"billingContact._info.contact_href\", \"company_companies\".\"invoiceToEmailAddress\" AS \"invoiceToEmailAddress\", \"company_companies\".\"billingSite.id\" AS \"billingSite.id\", \"company_companies\".\"billingSite.name\" AS \"billingSite.name\", \"company_companies\".\"billingSite._info.site_href\" AS \"billingSite._info.site_href\" FROM \"connectwise\".\"company_companies\" AS \"company_companies\" LIMIT 100"

    final_query=run_union_all(q1,q2)
    client = clickhouse_connect.get_client(
        host='xt5mi7p9ri.ap-south-1.aws.clickhouse.cloud',
        port=8443,  # Secure HTTPS port for ClickHouse Cloud
        username='default',  # Change if needed
        password='0UU4_qgtXSrC1',  # Replace with your actual password
        secure=True  # Required for ClickHouse Cloud
        # database='insightapps_dev'
    )
    final_query2="""
            SELECT 
                C.id AS company_id,
                H.id AS halops_id,
                C.identifier,
                C.name,
                C.status.id,
                C.status.name,
                C.status._info.status_href,
                C.country.id,
                C.country.name,
                C.country._info.country_href,
                C.phoneNumber,
                C.website,
                C.territory.id,
                C.territory.name,
                C.territory._info.location_href,
                C.market.id,
                C.market.name,
                C.market._info.Market_href,
                C.defaultContact.id,
                C.defaultContact.name,
                C.defaultContact._info.contact_href,
                C.dateAcquired,
                C.annualRevenue,
                C.timeZoneSetup.id,
                C.timeZoneSetup.name,
                C.timeZoneSetup._info.timeZoneSetup_href,
                C.leadFlag,
                C.unsubscribeFlag,
                C.taxCode.id,
                C.taxCode.name,
                C.taxCode._info.taxCode_href,
                C.billingTerms.id,
                C.billingTerms.name,
                C.billToCompany.id,
                C.billToCompany.identifier,
                C.billToCompany.name,
                C.billToCompany._info.company_href,
                C.invoiceDeliveryMethod.id,
                C.invoiceDeliveryMethod.name,
                C.deletedFlag,
                C.mobileGuid,
                C.isVendorFlag,
                C.site.id,
                C.site.name,
                C.site._info.site_href,
                C._info.lastUpdated,
                C._info.updatedBy,
                C._info.dateEntered,
                C._info.enteredBy,
                C._info.contacts_href,
                C._info.agreements_href,
                C._info.tickets_href,
                C._info.opportunities_href,
                C._info.activities_href,
                C._info.projects_href,
                C._info.configurations_href,
                C._info.orders_href,
                C._info.documents_href,
                C._info.sites_href,
                C._info.teams_href,
                C._info.reports_href,
                C._info.notes_href,
                H.created_at AS created_at_haloPs,
                H.updated_at AS updated_at_haloPs,
                H.user_id AS user_id_haloPs,
                H.site_url AS site_url_haloPs,
                H.client_id AS client_id_haloPs,
                H.client_secret AS client_secret_haloPs,
                H.access_token AS access_token_haloPs,
                H.display_name AS display_name_haloPs,
                H.expiry_date AS expiry_date_haloPs
            FROM 
            "connectwise"."company_companies" AS C
            INNER JOIN 
            "insightapps_dev"."HaloPs" AS H ON 1=1
    """
    result = client.query(final_query2)
    rows = result.result_rows
    columns = result.column_names
    datatypes = result.column_types
    final_list=[]
    for cl,rw in zip(columns,rows):
        final_list.append({'column':cl,'data':rw})
    return Response(final_list,status=status.HTTP_200_OK)