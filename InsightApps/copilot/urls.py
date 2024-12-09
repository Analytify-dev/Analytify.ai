from django.urls import path
from .views import *

urlpatterns = [
    # path('copilot1/<token>',GetServerTablesList.as_view(),name='Get Query Set Details'),
    path('validate-api-key/<token>', ValidateApiKeyView.as_view(), name='validate-api-key'),
    path('copilot/<token>',CopilotChartSuggestionAPI.as_view(),name='Get Chart Suggestions'),
]