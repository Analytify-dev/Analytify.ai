from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('',include('dashboard.urls')),
    path('',include('quickbooks.urls')),
    path('',include('template_dashboards.urls')),
    path('public/',include('dashboard.public_urls')),
    path('ai/',include('copilot.urls')),
]