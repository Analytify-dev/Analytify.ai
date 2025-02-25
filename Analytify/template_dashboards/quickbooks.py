import os,requests,pdfplumber,boto3,ast,random,re,secrets,string
from project import settings
import pandas as pd
from dashboard import views,models as dshb_models,Connections,columns_extract,clickhouse,Filters
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
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from base64 import b64encode
from django.test import Client,RequestFactory
from django.urls import reverse



def query_form(tok1,hierarchy_id,display_name):
    table_names=[[f'{display_name}', 'Account', 'Account'], [f'{display_name}', 'Customer', 'Customer'], [f'{display_name}', 'Invoice', 'Invoice']]
    # updated_data = [[(display_name if element == 'display_name' else element) for element in sublist] for sublist in table_names]
    quer_tb=dshb_models.QuerySets.objects.create(
        user_id=tok1['user_id'],
        hierarchy_id=hierarchy_id,
        table_names=table_names,
        join_type=['inner', 'inner'],
        joining_conditions=[[{'table1': 'Account', 'firstcolumn': 'LastUpdatedTime', 'operator': '=', 'secondcolumn': 'LastUpdatedTime', 'table2': 'Customer'}], [{'table1': 'Account', 'firstcolumn': 'LastUpdatedTime', 'operator': '=', 'secondcolumn': 'LastUpdatedTime', 'table2': 'Invoice'}]],
        is_custom_sql=False,
        is_sample=False,
        custom_query=f"""SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" 
                        FROM \"{display_name}\".\"Account\" AS \"Account\" 
                        INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" 
                        INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\";
                        """,
        query_name="template_Quickbooks_query",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        datasource_path=None,
        datasource_json=None
    )
    quer_tb.save()
    return quer_tb


def sheets_list(queryset_id,tok1,hierarchy_id,display_name):
    sheetFilterQuerySetData=[
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [' "City"'],
            "rows": [' "TxnId"'],
            "custom_query": f"""
                            SELECT \"City\" AS \"City\", \"TxnId\" AS \"TxnId\" 
                            FROM (
                                SELECT 
                                    \"Account\".\"Name\" AS \"Name\", 
                                    \"Account\".\"SubAccount\" AS \"SubAccount\", 
                                    \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", 
                                    \"Account\".\"Active\" AS \"Active\", 
                                    \"Account\".\"Classification\" AS \"Classification\", 
                                    \"Account\".\"AccountType\" AS \"AccountType\", 
                                    \"Account\".\"AccountSubType\" AS \"AccountSubType\", 
                                    \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", 
                                    \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", 
                                    \"Account\".\"value\" AS \"value\", 
                                    \"Account\".\"name_2\" AS \"name_2\", 
                                    \"Account\".\"domain\" AS \"domain\", 
                                    \"Account\".\"sparse\" AS \"sparse\", 
                                    \"Account\".\"Id\" AS \"Id\", 
                                    \"Account\".\"SyncToken\" AS \"SyncToken\", 
                                    \"Account\".\"CreateTime\" AS \"CreateTime\", 
                                    \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", 
                                    \"Account\".\"AcctNum\" AS \"AcctNum\", 
                                    \"Account\".\"startPosition\" AS \"startPosition\", 
                                    \"Account\".\"maxResults\" AS \"maxResults\", 
                                    \"Account\".\"time\" AS \"time\", 
                                    \"Customer\".\"Taxable\" AS \"Taxable\", 
                                    \"Customer\".\"Job\" AS \"Job\", 
                                    \"Customer\".\"BillWithParent\" AS \"BillWithParent\", 
                                    \"Customer\".\"Balance\" AS \"Balance\", 
                                    \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", 
                                    \"Customer\".\"value\" AS \"value(Customer)\", 
                                    \"Customer\".\"name\" AS \"name(Customer)\", 
                                    \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", 
                                    \"Customer\".\"IsProject\" AS \"IsProject\", 
                                    \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", 
                                    \"Customer\".\"domain\" AS \"domain(Customer)\", 
                                    \"Customer\".\"sparse\" AS \"sparse(Customer)\", 
                                    \"Customer\".\"Id\" AS \"Id(Customer)\", 
                                    \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", 
                                    \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", 
                                    \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", 
                                    \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", 
                                    \"Customer\".\"DisplayName\" AS \"DisplayName\", 
                                    \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", 
                                    \"Customer\".\"Active\" AS \"Active(Customer)\", 
                                    \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", 
                                    \"Customer\".\"Address\" AS \"Address\", 
                                    \"Customer\".\"Line1\" AS \"Line1\", 
                                    \"Customer\".\"City\" AS \"City\", 
                                    \"Customer\".\"Country\" AS \"Country\", 
                                    \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", 
                                    \"Customer\".\"PostalCode\" AS \"PostalCode\", 
                                    \"Customer\".\"Notes\" AS \"Notes\", 
                                    \"Customer\".\"Title\" AS \"Title\", 
                                    \"Customer\".\"GivenName\" AS \"GivenName\", 
                                    \"Customer\".\"MiddleName\" AS \"MiddleName\", 
                                    \"Customer\".\"FamilyName\" AS \"FamilyName\", 
                                    \"Customer\".\"Suffix\" AS \"Suffix\", 
                                    \"Customer\".\"CompanyName\" AS \"CompanyName\", 
                                    \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", 
                                    \"Customer\".\"Lat\" AS \"Lat\", 
                                    \"Customer\".\"Long\" AS \"Long\", 
                                    \"Customer\".\"URI\" AS \"URI\", 
                                    \"Customer\".\"Level\" AS \"Level\", 
                                    \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", 
                                    \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", 
                                    \"Customer\".\"time\" AS \"time(Customer)\", 
                                    \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", 
                                    \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", 
                                    \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", 
                                    \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", 
                                    \"Invoice\".\"domain\" AS \"domain(Invoice)\", 
                                    \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", 
                                    \"Invoice\".\"Id\" AS \"Id(Invoice)\", 
                                    \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", 
                                    \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", 
                                    \"Invoice\".\"value\" AS \"value(Invoice)\", 
                                    \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", 
                                    \"Invoice\".\"DocNumber\" AS \"DocNumber\", 
                                    \"Invoice\".\"TxnDate\" AS \"TxnDate\", 
                                    \"Invoice\".\"name\" AS \"name(Invoice)\", 
                                    \"Invoice\".\"TxnId\" AS \"TxnId\", 
                                    \"Invoice\".\"TxnType\" AS \"TxnType\", 
                                    \"Invoice\".\"LineNum\" AS \"LineNum\", 
                                    \"Invoice\".\"Description\" AS \"Description\", 
                                    \"Invoice\".\"Amount\" AS \"Amount\", 
                                    \"Invoice\".\"DetailType\" AS \"DetailType\", 
                                    \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", 
                                    \"Invoice\".\"Qty\" AS \"Qty\", 
                                    \"Invoice\".\"TotalTax\" AS \"TotalTax\", 
                                    \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", 
                                    \"Invoice\".\"DueDate\" AS \"DueDate\", 
                                    \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", 
                                    \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", 
                                    \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", 
                                    \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", 
                                    \"Invoice\".\"Address\" AS \"Address(Invoice)\", 
                                    \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", 
                                    \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", 
                                    \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", 
                                    \"Invoice\".\"PercentBased\" AS \"PercentBased\", 
                                    \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", 
                                    \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", 
                                    \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", 
                                    \"Invoice\".\"Line2\" AS \"Line2\", 
                                    \"Invoice\".\"City\" AS \"City(Invoice)\", 
                                    \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", 
                                    \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", 
                                    \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", 
                                    \"Invoice\".\"Long\" AS \"Long(Invoice)\", 
                                    \"Invoice\".\"Country\" AS \"Country(Invoice)\", 
                                    \"Invoice\".\"Line3\" AS \"Line3\", 
                                    \"Invoice\".\"Line4\" AS \"Line4\", 
                                    \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", 
                                    \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", 
                                    \"Invoice\".\"Value_2\" AS \"Value_2\", 
                                    \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", 
                                    \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", 
                                    \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", 
                                    \"Invoice\".\"totalCount\" AS \"totalCount\", 
                                    \"Invoice\".\"time\" AS \"time(Invoice)\"
                                FROM \"{display_name}\".\"Account\" AS \"Account\"
                                INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" 
                                    ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\"
                                INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" 
                                    ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\"
                            ) temp_table 
                            GROUP BY \"City\", \"City\", \"TxnId\" 
                            ORDER BY \"City\" NULLS FIRST
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [' "TotalTax"'],
            "rows": ['"sum(TotalAmt)"'],
            "custom_query": f"""
                            SELECT \"TotalTax\" AS \"TotalTax\", SUM(\"TotalAmt\") AS \"sum(TotalAmt)\" 
                            FROM (
                                SELECT 
                                    \"Account\".\"Name\" AS \"Name\", 
                                    \"Account\".\"SubAccount\" AS \"SubAccount\", 
                                    \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", 
                                    \"Account\".\"Active\" AS \"Active\", 
                                    \"Account\".\"Classification\" AS \"Classification\", 
                                    \"Account\".\"AccountType\" AS \"AccountType\", 
                                    \"Account\".\"AccountSubType\" AS \"AccountSubType\", 
                                    \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", 
                                    \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", 
                                    \"Account\".\"value\" AS \"value\", 
                                    \"Account\".\"name_2\" AS \"name_2\", 
                                    \"Account\".\"domain\" AS \"domain\", 
                                    \"Account\".\"sparse\" AS \"sparse\", 
                                    \"Account\".\"Id\" AS \"Id\", 
                                    \"Account\".\"SyncToken\" AS \"SyncToken\", 
                                    \"Account\".\"CreateTime\" AS \"CreateTime\", 
                                    \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", 
                                    \"Account\".\"AcctNum\" AS \"AcctNum\", 
                                    \"Account\".\"startPosition\" AS \"startPosition\", 
                                    \"Account\".\"maxResults\" AS \"maxResults\", 
                                    \"Account\".\"time\" AS \"time\", 
                                    \"Customer\".\"Taxable\" AS \"Taxable\", 
                                    \"Customer\".\"Job\" AS \"Job\", 
                                    \"Customer\".\"BillWithParent\" AS \"BillWithParent\", 
                                    \"Customer\".\"Balance\" AS \"Balance\", 
                                    \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", 
                                    \"Customer\".\"value\" AS \"value(Customer)\", 
                                    \"Customer\".\"name\" AS \"name(Customer)\", 
                                    \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", 
                                    \"Customer\".\"IsProject\" AS \"IsProject\", 
                                    \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", 
                                    \"Customer\".\"domain\" AS \"domain(Customer)\", 
                                    \"Customer\".\"sparse\" AS \"sparse(Customer)\", 
                                    \"Customer\".\"Id\" AS \"Id(Customer)\", 
                                    \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", 
                                    \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", 
                                    \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", 
                                    \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", 
                                    \"Customer\".\"DisplayName\" AS \"DisplayName\", 
                                    \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", 
                                    \"Customer\".\"Active\" AS \"Active(Customer)\", 
                                    \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", 
                                    \"Customer\".\"Address\" AS \"Address\", 
                                    \"Customer\".\"Line1\" AS \"Line1\", 
                                    \"Customer\".\"City\" AS \"City\", 
                                    \"Customer\".\"Country\" AS \"Country\", 
                                    \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", 
                                    \"Customer\".\"PostalCode\" AS \"PostalCode\", 
                                    \"Customer\".\"Notes\" AS \"Notes\", 
                                    \"Customer\".\"Title\" AS \"Title\", 
                                    \"Customer\".\"GivenName\" AS \"GivenName\", 
                                    \"Customer\".\"MiddleName\" AS \"MiddleName\", 
                                    \"Customer\".\"FamilyName\" AS \"FamilyName\", 
                                    \"Customer\".\"Suffix\" AS \"Suffix\", 
                                    \"Customer\".\"CompanyName\" AS \"CompanyName\", 
                                    \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", 
                                    \"Customer\".\"Lat\" AS \"Lat\", 
                                    \"Customer\".\"Long\" AS \"Long\", 
                                    \"Customer\".\"URI\" AS \"URI\", 
                                    \"Customer\".\"Level\" AS \"Level\", 
                                    \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", 
                                    \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", 
                                    \"Customer\".\"time\" AS \"time(Customer)\", 
                                    \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", 
                                    \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", 
                                    \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", 
                                    \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", 
                                    \"Invoice\".\"domain\" AS \"domain(Invoice)\", 
                                    \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", 
                                    \"Invoice\".\"Id\" AS \"Id(Invoice)\", 
                                    \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", 
                                    \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", 
                                    \"Invoice\".\"value\" AS \"value(Invoice)\", 
                                    \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", 
                                    \"Invoice\".\"DocNumber\" AS \"DocNumber\", 
                                    \"Invoice\".\"TxnDate\" AS \"TxnDate\", 
                                    \"Invoice\".\"name\" AS \"name(Invoice)\", 
                                    \"Invoice\".\"TxnId\" AS \"TxnId\", 
                                    \"Invoice\".\"TxnType\" AS \"TxnType\", 
                                    \"Invoice\".\"LineNum\" AS \"LineNum\", 
                                    \"Invoice\".\"Description\" AS \"Description\", 
                                    \"Invoice\".\"Amount\" AS \"Amount\", 
                                    \"Invoice\".\"DetailType\" AS \"DetailType\", 
                                    \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", 
                                    \"Invoice\".\"Qty\" AS \"Qty\", 
                                    \"Invoice\".\"TotalTax\" AS \"TotalTax\", 
                                    \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", 
                                    \"Invoice\".\"DueDate\" AS \"DueDate\", 
                                    \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", 
                                    \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", 
                                    \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", 
                                    \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", 
                                    \"Invoice\".\"Address\" AS \"Address(Invoice)\", 
                                    \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", 
                                    \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", 
                                    \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", 
                                    \"Invoice\".\"PercentBased\" AS \"PercentBased\", 
                                    \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", 
                                    \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", 
                                    \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", 
                                    \"Invoice\".\"Line2\" AS \"Line2\", 
                                    \"Invoice\".\"City\" AS \"City(Invoice)\", 
                                    \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", 
                                    \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", 
                                    \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", 
                                    \"Invoice\".\"Long\" AS \"Long(Invoice)\", 
                                    \"Invoice\".\"Country\" AS \"Country(Invoice)\", 
                                    \"Invoice\".\"Line3\" AS \"Line3\", 
                                    \"Invoice\".\"Line4\" AS \"Line4\", 
                                    \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", 
                                    \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", 
                                    \"Invoice\".\"Value_2\" AS \"Value_2\", 
                                    \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", 
                                    \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", 
                                    \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", 
                                    \"Invoice\".\"totalCount\" AS \"totalCount\", 
                                    \"Invoice\".\"time\" AS \"time(Invoice)\"
                                FROM \"{display_name}\".\"Account\" AS \"Account\"
                                INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" 
                                    ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\"
                                INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" 
                                    ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\"
                            ) temp_table 
                            GROUP BY \"TotalTax\", \"TotalTax\" 
                            ORDER BY \"TotalTax\" NULLS FIRST
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [' "name(Invoice)"', '"(TxnDate)"', ' "TxnType"', ' "Amount"', ' "TotalTax"', ' "Balance(Invoice)"', '"(DueDate)"'],
            "rows": [],
            "custom_query": f"""
                            SELECT \"name(Invoice)\" AS \"name(Invoice)\", DATE_FORMAT(CAST(\"TxnDate\" AS TIMESTAMP), '%Y-%m-%d %H:%M:%S') AS \"(TxnDate)\", \"TxnType\" AS \"TxnType\", \"Amount\" AS \"Amount\", \"TotalTax\" AS \"TotalTax\", \"Balance(Invoice)\" AS \"Balance(Invoice)\", DATE_FORMAT(CAST(\"DueDate\" AS TIMESTAMP), '%Y-%m-%d %H:%M:%S') AS \"(DueDate)\" 
                            FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" 
                            FROM \"{display_name}\".\"Account\" AS \"Account\" 
                            INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" 
                            INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table 
                            GROUP BY \"name(Invoice)\", \"(TxnDate)\", \"TxnType\", \"Amount\", \"TotalTax\", \"Balance(Invoice)\", \"(DueDate)\", \"name(Invoice)\", \"(TxnDate)\", \"TxnType\", \"Amount\", \"TotalTax\", \"Balance(Invoice)\", \"(DueDate)\" 
                            ORDER BY \"name(Invoice)\" NULLS FIRST
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [' "name(Invoice)"'],
            "rows": ['"sum(Balance(Invoice))"'],
            "custom_query": f"""
                                SELECT \"name(Invoice)\" AS \"name(Invoice)\", SUM(\"Balance(Invoice)\") AS \"sum(Balance(Invoice))\" 
                                FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" 
                                FROM \"{display_name}\".\"Account\" AS \"Account\" 
                                INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" 
                                INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table 
                                GROUP BY \"name(Invoice)\", \"name(Invoice)\" 
                                ORDER BY \"name(Invoice)\" NULLS FIRST
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [' "Country"'],
            "rows": ['"sum(Balance)"'],
            "custom_query": f"""
                            SELECT \"Country\" AS \"Country\", SUM(\"Balance\") AS \"sum(Balance)\" 
                            FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" 
                            FROM \"{display_name}\".\"Account\" AS \"Account\" 
                            INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" 
                            INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table 
                            GROUP BY \"Country\", \"Country\" 
                            ORDER BY \"Country\" NULLS FIRST
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": [' "CNTD(TxnId)"'],
            "custom_query": f"""
                            SELECT COUNT(DISTINCT \"TxnId\") AS \"CNTD(TxnId)\" 
                            FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" 
                            FROM \"{display_name}\".\"Account\" AS \"Account\" 
                            INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" 
                            INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table 
                            ORDER BY 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": [' "CNTD(Active)"'],
            "custom_query": f"""
                            SELECT COUNT(DISTINCT \"Active\") AS \"CNTD(Active)\" FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" FROM \"{display_name}\".\"Account\" AS \"Account\" INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table ORDER BY 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": [' "Id"'],
            "custom_query": f"""
                            SELECT \"Id\" AS \"Id\" FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" FROM \"{display_name}\".\"Account\" AS \"Account\" INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table GROUP BY \"Id\" ORDER BY 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": ['"sum(CurrentBalance)"'],
            "custom_query": f"""
                            SELECT SUM(\"CurrentBalance\") AS \"sum(CurrentBalance)\" FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" FROM \"{display_name}\".\"Account\" AS \"Account\" INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table order by 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": [' "CNTD(Active(Customer))"'],
            "custom_query": f"""
                            SELECT COUNT(DISTINCT \"Active(Customer)\") AS \"CNTD(Active(Customer))\" FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" FROM \"{display_name}\".\"Account\" AS \"Account\" INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table order by 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "datasource_querysetid": "",
            "queryset_id": queryset_id,
            "user_id": tok1['user_id'],
            "hierarchy_id": hierarchy_id,
            "filter_id_list": [],
            "columns": [],
            "rows": [' "Id(Customer)"'],
            "custom_query": f"""
                            SELECT \"Id(Customer)\" AS \"Id(Customer)\" FROM (SELECT \"Account\".\"Name\" AS \"Name\", \"Account\".\"SubAccount\" AS \"SubAccount\", \"Account\".\"FullyQualifiedName\" AS \"FullyQualifiedName\", \"Account\".\"Active\" AS \"Active\", \"Account\".\"Classification\" AS \"Classification\", \"Account\".\"AccountType\" AS \"AccountType\", \"Account\".\"AccountSubType\" AS \"AccountSubType\", \"Account\".\"CurrentBalance\" AS \"CurrentBalance\", \"Account\".\"CurrentBalanceWithSubAccounts\" AS \"CurrentBalanceWithSubAccounts\", \"Account\".\"value\" AS \"value\", \"Account\".\"name_2\" AS \"name_2\", \"Account\".\"domain\" AS \"domain\", \"Account\".\"sparse\" AS \"sparse\", \"Account\".\"Id\" AS \"Id\", \"Account\".\"SyncToken\" AS \"SyncToken\", \"Account\".\"CreateTime\" AS \"CreateTime\", \"Account\".\"LastUpdatedTime\" AS \"LastUpdatedTime\", \"Account\".\"AcctNum\" AS \"AcctNum\", \"Account\".\"startPosition\" AS \"startPosition\", \"Account\".\"maxResults\" AS \"maxResults\", \"Account\".\"time\" AS \"time\", \"Customer\".\"Taxable\" AS \"Taxable\", \"Customer\".\"Job\" AS \"Job\", \"Customer\".\"BillWithParent\" AS \"BillWithParent\", \"Customer\".\"Balance\" AS \"Balance\", \"Customer\".\"BalanceWithJobs\" AS \"BalanceWithJobs\", \"Customer\".\"value\" AS \"value(Customer)\", \"Customer\".\"name\" AS \"name(Customer)\", \"Customer\".\"PreferredDeliveryMethod\" AS \"PreferredDeliveryMethod\", \"Customer\".\"IsProject\" AS \"IsProject\", \"Customer\".\"ClientEntityId\" AS \"ClientEntityId\", \"Customer\".\"domain\" AS \"domain(Customer)\", \"Customer\".\"sparse\" AS \"sparse(Customer)\", \"Customer\".\"Id\" AS \"Id(Customer)\", \"Customer\".\"SyncToken\" AS \"SyncToken(Customer)\", \"Customer\".\"CreateTime\" AS \"CreateTime(Customer)\", \"Customer\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Customer)\", \"Customer\".\"FullyQualifiedName\" AS \"FullyQualifiedName(Customer)\", \"Customer\".\"DisplayName\" AS \"DisplayName\", \"Customer\".\"PrintOnCheckName\" AS \"PrintOnCheckName\", \"Customer\".\"Active\" AS \"Active(Customer)\", \"Customer\".\"V4IDPseudonym\" AS \"V4IDPseudonym\", \"Customer\".\"Address\" AS \"Address\", \"Customer\".\"Line1\" AS \"Line1\", \"Customer\".\"City\" AS \"City\", \"Customer\".\"Country\" AS \"Country\", \"Customer\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode\", \"Customer\".\"PostalCode\" AS \"PostalCode\", \"Customer\".\"Notes\" AS \"Notes\", \"Customer\".\"Title\" AS \"Title\", \"Customer\".\"GivenName\" AS \"GivenName\", \"Customer\".\"MiddleName\" AS \"MiddleName\", \"Customer\".\"FamilyName\" AS \"FamilyName\", \"Customer\".\"Suffix\" AS \"Suffix\", \"Customer\".\"CompanyName\" AS \"CompanyName\", \"Customer\".\"FreeFormNumber\" AS \"FreeFormNumber\", \"Customer\".\"Lat\" AS \"Lat\", \"Customer\".\"Long\" AS \"Long\", \"Customer\".\"URI\" AS \"URI\", \"Customer\".\"Level\" AS \"Level\", \"Customer\".\"startPosition\" AS \"startPosition(Customer)\", \"Customer\".\"maxResults\" AS \"maxResults(Customer)\", \"Customer\".\"time\" AS \"time(Customer)\", \"Invoice\".\"AllowIPNPayment\" AS \"AllowIPNPayment\", \"Invoice\".\"AllowOnlinePayment\" AS \"AllowOnlinePayment\", \"Invoice\".\"AllowOnlineCreditCardPayment\" AS \"AllowOnlineCreditCardPayment\", \"Invoice\".\"AllowOnlineACHPayment\" AS \"AllowOnlineACHPayment\", \"Invoice\".\"domain\" AS \"domain(Invoice)\", \"Invoice\".\"sparse\" AS \"sparse(Invoice)\", \"Invoice\".\"Id\" AS \"Id(Invoice)\", \"Invoice\".\"SyncToken\" AS \"SyncToken(Invoice)\", \"Invoice\".\"CreateTime\" AS \"CreateTime(Invoice)\", \"Invoice\".\"value\" AS \"value(Invoice)\", \"Invoice\".\"LastUpdatedTime\" AS \"LastUpdatedTime(Invoice)\", \"Invoice\".\"DocNumber\" AS \"DocNumber\", \"Invoice\".\"TxnDate\" AS \"TxnDate\", \"Invoice\".\"name\" AS \"name(Invoice)\", \"Invoice\".\"TxnId\" AS \"TxnId\", \"Invoice\".\"TxnType\" AS \"TxnType\", \"Invoice\".\"LineNum\" AS \"LineNum\", \"Invoice\".\"Description\" AS \"Description\", \"Invoice\".\"Amount\" AS \"Amount\", \"Invoice\".\"DetailType\" AS \"DetailType\", \"Invoice\".\"UnitPrice\" AS \"UnitPrice\", \"Invoice\".\"Qty\" AS \"Qty\", \"Invoice\".\"TotalTax\" AS \"TotalTax\", \"Invoice\".\"FreeFormAddress\" AS \"FreeFormAddress\", \"Invoice\".\"DueDate\" AS \"DueDate\", \"Invoice\".\"TotalAmt\" AS \"TotalAmt\", \"Invoice\".\"ApplyTaxAfterDiscount\" AS \"ApplyTaxAfterDiscount\", \"Invoice\".\"PrintStatus\" AS \"PrintStatus\", \"Invoice\".\"EmailStatus\" AS \"EmailStatus\", \"Invoice\".\"Address\" AS \"Address(Invoice)\", \"Invoice\".\"Balance\" AS \"Balance(Invoice)\", \"Invoice\".\"DeliveryType\" AS \"DeliveryType\", \"Invoice\".\"DeliveryTime\" AS \"DeliveryTime\", \"Invoice\".\"PercentBased\" AS \"PercentBased\", \"Invoice\".\"TaxPercent\" AS \"TaxPercent\", \"Invoice\".\"NetAmountTaxable\" AS \"NetAmountTaxable\", \"Invoice\".\"Line1\" AS \"Line1(Invoice)\", \"Invoice\".\"Line2\" AS \"Line2\", \"Invoice\".\"City\" AS \"City(Invoice)\", \"Invoice\".\"CountrySubDivisionCode\" AS \"CountrySubDivisionCode(Invoice)\", \"Invoice\".\"PostalCode\" AS \"PostalCode(Invoice)\", \"Invoice\".\"Lat\" AS \"Lat(Invoice)\", \"Invoice\".\"Long\" AS \"Long(Invoice)\", \"Invoice\".\"Country\" AS \"Country(Invoice)\", \"Invoice\".\"Line3\" AS \"Line3\", \"Invoice\".\"Line4\" AS \"Line4\", \"Invoice\".\"ServiceDate\" AS \"ServiceDate\", \"Invoice\".\"DiscountPercent\" AS \"DiscountPercent\", \"Invoice\".\"Value_2\" AS \"Value_2\", \"Invoice\".\"PrivateNote\" AS \"PrivateNote\", \"Invoice\".\"startPosition\" AS \"startPosition(Invoice)\", \"Invoice\".\"maxResults\" AS \"maxResults(Invoice)\", \"Invoice\".\"totalCount\" AS \"totalCount\", \"Invoice\".\"time\" AS \"time(Invoice)\" FROM \"{display_name}\".\"Account\" AS \"Account\" INNER JOIN \"{display_name}\".\"Customer\" AS \"Customer\" ON \"Account\".\"LastUpdatedTime\" = \"Customer\".\"LastUpdatedTime\" INNER JOIN \"{display_name}\".\"Invoice\" AS \"Invoice\" ON \"Account\".\"LastUpdatedTime\" = \"Invoice\".\"LastUpdatedTime\") temp_table GROUP BY \"Id(Customer)\" order by 1
                            """,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
    ]
    try:
        for entry in sheetFilterQuerySetData:
            sheetfilter_table_create=dshb_models.SheetFilter_querysets.objects.create(
                datasource_querysetid=int(entry.get("datasource_querysetid") or 0) if entry.get("datasource_querysetid") else None,
                queryset_id=int(entry.get("queryset_id") or 0) if entry.get("queryset_id") else None,
                user_id=entry.get("user_id"),
                hierarchy_id=int(entry.get("hierarchy_id") or 0) if entry.get("hierarchy_id") else None,
                filter_id_list=json.dumps(entry.get("filter_id_list", [])),
                columns=json.dumps(entry.get("columns", [])),
                rows=json.dumps(entry.get("rows", [])),
                custom_query=entry.get("custom_query"),
                created_at=entry.get("created_at", datetime.datetime.now()),
                updated_at=entry.get("updated_at", datetime.datetime.now()),
            )
            sheetfilter_table_create.save()
        # self.stdout.write(self.style.SUCCESS('Successfully imported data into SheetFilter QuerySet'))
    except Exception as e:
        pass
    sheet_filter_queryset_ids_list = dshb_models.SheetFilter_querysets.objects.filter(user_id=tok1['user_id'], queryset_id=queryset_id).values_list('Sheetqueryset_id', flat=True).order_by('Sheetqueryset_id')
    return sheetfilter_table_create,sheet_filter_queryset_ids_list


def sheets_data(queryset_id,tok1,hierarchy_id,display_name):
    sheet_filter_table,sheet_filter_querysets=sheets_list(queryset_id,tok1,hierarchy_id,display_name)
    print("sheet_fl_ids",sheet_filter_querysets)
    sheetData = [
        {
            "user_id": tok1['user_id'],
            "chart_id": 27,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "City wise Transactions",
            "sheetfilter_querysets_id": sheet_filter_querysets[0],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>City wise Transactions</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 10,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Total Amount vs Tax",
            "sheetfilter_querysets_id": sheet_filter_querysets[1],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Total Amount vs Tax</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 1,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Customer Overview",
            "sheetfilter_querysets_id": sheet_filter_querysets[2],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Customer Overview</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 6,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Account wise Balance",
            "sheetfilter_querysets_id": sheet_filter_querysets[3],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Account wise Balance</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 29,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Country Wise Balance",
            "sheetfilter_querysets_id": sheet_filter_querysets[4],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Country Wise Balance</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Total Transactions",
            "sheetfilter_querysets_id": sheet_filter_querysets[5],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Total Transactions</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Active Accounts",
            "sheetfilter_querysets_id": sheet_filter_querysets[6],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Active Accounts</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Total Accounts",
            "sheetfilter_querysets_id": sheet_filter_querysets[7],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Total Accounts</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Account Balance",
            "sheetfilter_querysets_id": sheet_filter_querysets[8],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Account Balance</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Active Customers",
            "sheetfilter_querysets_id": sheet_filter_querysets[9],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Active Customers</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
        {
            "user_id": tok1['user_id'],
            "chart_id": 25,
            "hierarchy_id": hierarchy_id,
            "queryset_id": queryset_id,
            "filter_ids": [],
            "sheet_name": "Total Customers",
            "sheetfilter_querysets_id": sheet_filter_querysets[10],
            "datapath": '',
            "datasrc": "",
            "sheet_tag_name": """<p>Total Customers</p>""",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now()
        },
    ]
    try:
        for data in sheetData:
            sheet_data_instance = dshb_models.sheet_data(
                user_id=data['user_id'],
                chart_id=data['chart_id'],
                hierarchy_id=data['hierarchy_id'],
                is_sample=False,
                queryset_id=data['queryset_id'],
                filter_ids=data['filter_ids'],
                sheet_name=data['sheet_name'],
                sheet_filt_id=data['sheetfilter_querysets_id'],
                datapath=data['datapath'],
                datasrc=data['datasrc'],
                sheet_tag_name=data['sheet_tag_name'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
            )
            sheet_data_instance.save()
    except Exception as e:
        pass
    # return sheet_data_instance
    sheet_ids_list = list(dshb_models.sheet_data.objects.filter(user_id=tok1['user_id'], queryset_id=queryset_id).values_list('id', flat=True).order_by('-id'))
    return sheet_data_instance,sheet_ids_list


def dashbaord_data(queryset_id,tok1,hierarchy_id,sheet_ids_list):
    dashb_tb = dshb_models.dashboard_data.objects.create(
        user_id=tok1['user_id'],
        hierarchy_id=[hierarchy_id],
        queryset_id=queryset_id,
        sheet_ids=sheet_ids_list,
        selected_sheet_ids=sheet_ids_list,
        height=None,
        width=None,
        grid_id=1,
        is_sample=False,
        role_ids=[],
        user_ids=[],
        dashboard_name="templ_quickbooks",
        datapath='',
        datasrc='',
        imagepath='',
        imagesrc='',
        dashboard_tag_name="""<p>templ_quickbooks</p>""",
        is_public=False,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        )
    dashb_tb.save()
    return dashb_tb



def dashboard_data_main(sheets_ids_list,parameter,cursor,tok1,dashboard_table):
    sheets_final_data=[]
    for shid in sheets_ids_list:
        col_data=[]
        row_data=[]
        sh_tb=dshb_models.sheet_data.objects.get(id=shid)
        sh_fltr_tb=dshb_models.SheetFilter_querysets.objects.get(Sheetqueryset_id=sh_tb.sheet_filt_id)
        fn_query=sh_fltr_tb.custom_query.replace('\\','')
        result = cursor.execute(text(fn_query))
        if parameter.upper()=="MICROSOFTSQLSERVER":
            columns_info = cursor.description
            column_list = [column[0] for column in columns_info]
            rows = result.fetchall()
        else:
            column_names = result.keys()
            column_list = [column for column in column_names]
            rows = result.fetchall()
        transposed_rows = list(zip(*rows))
        for col,row in zip(column_list,transposed_rows):
            data = {
                "column":col,
                "data":list(row)
            }
            tb_col=[item.strip().strip('"') for item in Connections.litera_eval(sh_fltr_tb.columns)]
            tb_row=[item.strip().strip('"') for item in Connections.litera_eval(sh_fltr_tb.rows)]
            if col in tb_col:
                col_data.append(data)
            elif col in tb_row:
                row_data.append(data)
            else:
                pass
            # final_data.append(data)
        final_data = {'columns_data':col_data,'rows_data':row_data}

        ch_list=[]
        for ch in ast.literal_eval(sh_tb.filter_ids):
            ch_filter=dshb_models.ChartFilters.objects.filter(filter_id=ch).values()
            ch_list.append(ch_filter)
        flat_filters_data = [item for sublist in ch_list for item in sublist]

        if sh_tb.datasrc==None or sh_tb.datasrc=='' or sh_tb.datasrc=="":
            sheet_data=None
        else:
            data=requests.get(sh_tb.datasrc)
            sheet_data=data.json() 
        d1 = {
            "sheet_id":sh_tb.id,
            "sheet_name":sh_tb.sheet_name,
            "chart_id":sh_tb.chart_id,
            "hierarchy_id":sh_tb.hierarchy_id,
            "sheet_tag_name":sh_tb.sheet_tag_name,
            "sheet_data":sheet_data,
            "queryset_id":sh_tb.queryset_id,
            "created_by":tok1['user_id'],
            "sheet_filter_ids":Connections.litera_eval(sh_tb.filter_ids),
            "sheet_filter_quereyset_ids":sh_tb.sheet_filt_id,
            "datasource_queryset_id":sh_fltr_tb.datasource_querysetid,
            "filters_data":flat_filters_data,
            "custom_query":sh_fltr_tb.custom_query,
            "col_data":Connections.litera_eval(sh_fltr_tb.columns),
            "row_data":Connections.litera_eval(sh_fltr_tb.rows),
            "created_by":sh_tb.user_id,
            "sheet_query_data":final_data
        }
        if dashboard_table.datasrc==None or dashboard_table.datasrc=='' or dashboard_table.datasrc=="":
            dashboard_data=None
        else:
            data=requests.get(dashboard_table.datasrc)
            dashboard_data=data.json() 
        # gr_tb=dshb_models.grid_type.objects.get(id=dashboard_table.grid_id)
        sheet_name=[]
        if dashboard_table.sheet_ids==[] or dashboard_table.sheet_ids==None or dashboard_table.sheet_ids=='':
            sheet_name=[]
        else:
            try:
                for shid in ast.literal_eval(dashboard_table.sheet_ids):
                    try:
                        shdt=dshb_models.sheet_data.objects.get(id=shid)
                    except:
                        return Response({'message':'Sheet {} not exists'.format(shid)},status=status.HTTP_404_NOT_FOUND)
                    sheet_name.append(shdt.sheet_name)
            except:
                for shid in dashboard_table.sheet_ids:
                    try:
                        shdt=dshb_models.sheet_data.objects.get(id=shid)
                    except:
                        return Response({'message':'Sheet {} not exists'.format(shid)},status=status.HTTP_404_NOT_FOUND)
                    sheet_name.append(shdt.sheet_name)
        try:
            role_ids = Connections.litera_eval(dashboard_table.role_ids)
            user_ids = Connections.litera_eval(dashboard_table.user_ids)
        except:
            role_ids = dashboard_table.role_ids
            user_ids = dashboard_table.user_ids
        if role_ids=="" or role_ids=='':
            role_ids=[]
        if user_ids=="" or user_ids=='':
            user_ids=[]
        # dashbaord data
        d2 = {
            "dashboard_id":dashboard_table.id,
            "is_public":dashboard_table.is_public,
            "is_sample" : dashboard_table.is_sample,
            "dashboard_name":dashboard_table.dashboard_name,
            "dashboard_tag_name":dashboard_table.dashboard_tag_name,
            "sheet_ids":dashboard_table.sheet_ids,
            "selected_sheet_ids":dashboard_table.selected_sheet_ids,
            "sheet_names":sheet_name,
            "grid_type":None,
            "height":dashboard_table.height,
            "width":dashboard_table.width,
            "hierarchy_id":dashboard_table.hierarchy_id,
            "queryset_id":dashboard_table.queryset_id,
            "dashboard_image":dashboard_table.imagesrc,
            "dashboard_data":dashboard_data,
            "role_ids":role_ids,
            "user_ids":user_ids
        }
        sheets_final_data.append(d1)
        # new_resp={"sheets":sheets_final_data,"dashboard":d2}
    return sheets_final_data



def temp_dashb_main(tok1,database_name,query_table,sheets_table,sheets_ids_list,dashboard_table,parameter):
    try:
        clickhouse_class = clickhouse.Clickhouse(database_name)
        engine=clickhouse_class.engine
        cursor=clickhouse_class.cursor
    except:
        return Response({'message':"Connection closed, try again"},status=status.HTTP_406_NOT_ACCEPTABLE)
    dashb_main=dashboard_data_main(sheets_ids_list,parameter,cursor,tok1,dashboard_table)
    return Response(dashb_main,status=status.HTTP_200_OK)
    
    

@api_view(['GET'])
@transaction.atomic
@csrf_exempt
def quickbooks_dashbaord(request,hierarchy_id,token):
    if request.method=='GET':
        tok1 = views.test_token(token)
        if tok1['status']==200:
            try:
                dis_name,para=Connections.display_name(hierarchy_id)
                database_name=dis_name.display_name
            except:
                return Response({'message':'Invalid Id'},status=status.HTTP_404_NOT_FOUND)
            query_table=query_form(tok1,hierarchy_id,database_name)
            sheets_table,sheets_ids_list=sheets_data(query_table.queryset_id,tok1,hierarchy_id,database_name)
            dashboard_table=dashbaord_data(query_table.queryset_id,tok1,hierarchy_id,sheets_ids_list)
            pr_ids=dshb_models.parent_ids.objects.get(id=hierarchy_id)
            print("queryset_id",query_table.queryset_id)
            print("sheet_ids",sheets_ids_list)
            print("dashboard_id",dashboard_table.id)
            if pr_ids.parameter.upper()=="SERVER":
                srdt=dshb_models.ServerDetails.objects.get(id=pr_ids.table_id)
                srtp=dshb_models.ServerType.objects.get(id=srdt.server_type)
                parameter=srtp.server_type.upper()
            else:
                parameter=pr_ids.parameter.upper()
            dashb_data=temp_dashb_main(tok1,database_name,query_table,sheets_table,sheets_ids_list,dashboard_table,parameter)
            return dashb_data
        else:
            return Response(tok1,status=tok1['status'])
    else:
        return Response({'message':'Method not allowed'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
                # print(shid, sh_tb.sheet_name)
                # print(column_data)
                # print(rows_data)
                # payload = {
                #     "col":Connections.litera_eval(sh_fltr_tb.columns),
                #     "row":Connections.litera_eval(sh_fltr_tb.rows),
                #     "queryset_id":query_table.queryset_id,
                #     "datasource_querysetid":sh_fltr_tb.datasource_querysetid,
                #     "filter_id":Connections.litera_eval(sh_fltr_tb.filter_id_list),
                #     "hierarchy_id":hierarchy_id,
                #     "drill_down":[],
                #     "next_drill_down":None,
                #     "is_date":False,
                #     "hierarchy":[],
                #     "parent_user":None,
                #     "page_count":settings.perpage,
                #     "order_column":None
                # }
                # headers = {
                #     "Content-Type": "application/json"
                # }
                # local_url = 'http://127.0.0.1:8000'
                # url = f'{local_url}/v1/multi_col_dk/{token}'
                # response = requests.post(url, json=payload)
                # print(response)
                # print(response.status_code)
                # print(response.json())
            # dashbaord_table=dashbaord_data(query_table.queryset_id,tok1,hierarchy_id,sheets_ids_list)