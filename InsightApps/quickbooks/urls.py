from django.urls import path
from quickbooks import views,endpoints_data,salesforce,salesforce_endpoints

urlpatterns = [
    #### sales force
    path('salesforce/<token>',salesforce.authentication_salesforce,name='sales force authentication'),
    path('callback/<token>',salesforce.callback_api.as_view(),name='call back'),
    path('sales_user_details/<sf_id>/<token>',salesforce_endpoints.get_salesforce_user_info,name='user details'),
    path('refresh_token/<sf_id>/<token>',salesforce.refresh_access_token,name='refresh token'),
    path('salesforce_disconnection/<sf_id>/<token>',salesforce.qb_salesforce,name='salesforce disconnection'),

    #### authentication
    path('quickbooks/<token>',views.authentication_quickbooks,name='quickbooks authentication'),
    path('quickbooks_token/<token>',views.token_api.as_view(),name='token fetch'),
    path('user_details/<qb_id>/<token>',views.get_quickbooks_user_info,name='user details'),
    path('quickbooks_disconnection/<qb_id>/<token>',views.qb_disconnection,name='quickbooks disconnection'),

    #### data_reload
    path('data_reload/<qb_id>/<token>',views.qb_data_reload,name='data reload'),

    ##### Endpoints data
    path('balance_sheet/<qb_id>/<token>',endpoints_data.fetch_Balancesheet_details.as_view(),name='Balance sheet'),
    path('profitandloss/<qb_id>/<token>',endpoints_data.fetch_profitloss_details.as_view(),name='profit and loss'),
    path('accountsdetails/<qb_id>/<token>',endpoints_data.fetch_quickbooks_account,name='account details'),
    path('billdetails/<qb_id>/<token>',endpoints_data.fetch_Bill_details,name='bill details'),
    path('companydetails/<qb_id>/<token>',endpoints_data.fetch_company_details,name='company details'),
    path('customerdetails/<qb_id>/<token>',endpoints_data.fetch_customer_details,name='customer details'),
    path('employeedetails/<qb_id>/<token>',endpoints_data.fetch_employee_details,name='employee details'),
    path('estimatedetails/<qb_id>/<token>',endpoints_data.fetch_estimate_details,name='estimate details'),
    path('invoicedetails/<qb_id>/<token>',endpoints_data.fetch_invoice_details,name='invoice details'),
    path('itemdetails/<qb_id>/<token>',endpoints_data.fetch_item_details,name='item details'),
    path('paymentdetails/<qb_id>/<token>',endpoints_data.fetch_payment_details,name='payment details'),
    path('preferencedetails/<qb_id>/<token>',endpoints_data.fetch_Preferences_details,name='preference details'),
    path('taxagencydetails/<qb_id>/<token>',endpoints_data.fetch_TaxAgency_details,name='tax agency details'),
    path('vendordetails/<qb_id>/<token>',endpoints_data.fetch_vendor_details,name='vendor details'),

    ##### Salesforce endpoints
    path('sf_tables_list/<sf_id>/<token>',salesforce_endpoints.to_fetch_all_tables_details,name='salesforce all tables list'),
    path('accounts_data/<sf_id>/<token>',salesforce_endpoints.accounts_data,name='salesforce accounts data'),

    #### Query_data
    path('qs_query_data/<token>',salesforce_endpoints.query_data.as_view(),name='query data'),
]
