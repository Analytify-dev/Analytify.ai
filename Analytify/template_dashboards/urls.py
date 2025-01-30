from django.urls import path
from template_dashboards import quickbooks,connectwise,halops,salesforce

urlpatterns = [
    path('quickbooks_dashboard/<int:hierarchy_id>/<token>',quickbooks.quickbooks_dashbaord,name='quickbooks_dashbaord'),
    path('connectwise_dashboard/<int:hierarchy_id>/<token>',connectwise.connectwise_dashbaord,name='connectwise_dashboard'),
    path('halops_dashboard/<int:hierarchy_id>/<token>',halops.halops_dashbaord,name='halops_dashboard'),
    path('salesforce_dashbaord/<int:hierarchy_id>/<token>',salesforce.salesforce_dashbaord,name='salesforce_dashbaord'),
]
