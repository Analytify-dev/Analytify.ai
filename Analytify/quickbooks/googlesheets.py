from django.utils.timezone import now
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from project import settings
from quickbooks.models import TokenStoring
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
import urllib.parse
from datetime import timedelta
from dashboard.views import test_token
from django.db import transaction
from dashboard.models import parent_ids,UserProfile
import json
import pandas as pd
from dashboard.clickhouse import Clickhouse
from dashboard import clickhouse
from sqlalchemy import text
import numpy as np
from datetime import datetime
from oauth2_provider.models import AccessToken
import re

# Constants for status messages
ERROR_AUTH_CODE_MISSING = {"error": "Authorization code not provided"}
ERROR_AUTH_REQUIRED = {"error": "Authentication required"}
ERROR_TOKEN_RETRIEVAL = {"error": "Failed to retrieve access token"}
ERROR_TOKEN_REFRESH_FAILED = {"error": "Failed to refresh access token"}

class GoogleAuthView(APIView):
    def get(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] == 200:
            params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": " ".join(settings.GOOGLE_AUTH_SCOPE),
                "access_type": "offline",
                "prompt": "consent",
            }
            auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
            return Response({"redirection_url": auth_url}, status=status.HTTP_200_OK)
        return Response(tok1, status=tok1['status'])
    
    def get_new_redirect_url(self, request):
        # Generate the new redirect URL here
        # This may involve creating a new authorization code, etc.
        # The exact implementation depends on your requirements
        params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": " ".join(settings.GOOGLE_AUTH_SCOPE),
                "access_type": "offline",
                "prompt": "consent",
            }
        new_redirect_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
        return new_redirect_url


class RefreshAccessToken:
    @staticmethod
    def refresh(user_id, parameter="google_sheets", token_id=None):
        # Fetch the token entry for the specified user and parameter
        token_entry = TokenStoring.objects.filter(user=user_id, parameter="google_sheets", id=token_id).first()
        
        if not token_entry:
            return None  # Return None if no token entry exists
        
        if token_entry.expiry_date <= now():
            # Prepare the token refresh request to Google's OAuth2 endpoint
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": token_entry.refreshtoken,
                "grant_type": "refresh_token",
            }
            
            response = requests.post(token_url, json=data)
            new_tokens = response.json()

            if "access_token" in new_tokens:
                # If the response contains an access token, update the stored token entry
                token_entry.accesstoken = new_tokens["access_token"]
                token_entry.expiry_date = now() + timedelta(seconds=new_tokens["expires_in"])
                token_entry.save()
                return new_tokens["access_token"]
        
        # If the token is still valid, return the existing access token
        return token_entry.accesstoken if token_entry else None

# Define Serializer
class GoogleAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True,
                                 help_text="Authorization code received from Google OAuth flow.")


class GoogleAuthSheetsView(CreateAPIView):
    serializer_class = GoogleAuthCodeSerializer

    @transaction.atomic()
    def post(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']  # Access validated code
        # Parse the URL
        parsed_url = urllib.parse.urlparse(code)

        # Get the query parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Get the code value
        code = query_params.get('code', [''])[0]

        if not code:
            return Response({"message": "No authorization code found in the provided URL"}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange the code for an access token
        if code:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            try:

                response = requests.post(token_url, json=data)
                tokens = response.json()
            except Exception as e:
                return Response({"message": tokens.get("error", "Failed to retrieve access token"), "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

            if "access_token" not in tokens:
                if tokens.get("error") == 'invalid_grant':
                    # If invalid_grant, generate a new redirect URL
                    view = GoogleAuthView()
                    new_redirect_url = view.get_new_redirect_url(request=request)
                    return Response({"message": "Invalid grant, please re-authorize", "redirect_url": new_redirect_url}, status=status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    return Response(
                        {"message": tokens.get("error", "Failed to retrieve access token"),
                        "error_description": tokens.get("error_description", "")},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            token_storing = TokenStoring.objects.create(
                user=tok1['user_id'],
                parameter="google_sheets",
                accesstoken=tokens["access_token"],
                refreshtoken=tokens.get("refresh_token", ""),
                idtoken=tokens.get("id_token", ""),
                tokentype=tokens.get("token_type", ""),
                expiry_date=now() + timedelta(seconds=tokens["expires_in"]),
            )

            pid = parent_ids.objects.create(
                table_id=token_storing.id,
                parameter="google_sheets"
            )

        access_token = RefreshAccessToken.refresh(tok1['user_id'], "google_sheets", token_storing.id)
        if not access_token:
            return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            creds = Credentials(token=access_token)
            drive_service = build("drive", "v3", credentials=creds)
            sheets_service = build("sheets", "v4", credentials=creds)

            results = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)"
            ).execute()

            spreadsheet_data = []
            for spreadsheet in results.get("files", []):
                try:
                    spreadsheet_data.append({
                        "id": spreadsheet["id"],
                        "name": spreadsheet["name"],
                        "mimeType": 'Spreadsheet' if spreadsheet["mimeType"] == 'application/vnd.google-apps.spreadsheet' else spreadsheet["mimeType"],
                        "createdTime": spreadsheet["createdTime"],
                        "modifiedTime": spreadsheet["modifiedTime"],
                        "size": spreadsheet.get("size", "Unknown"),
                    })
                except Exception as e:
                    print(f"Error fetching sheet names: {str(e)}")
                    return Response({"message": "Error accessing Google Sheets or Drive", "details": str(e)}, status=500)
            name,email = get_user_info_from_google(creds)
            profile = {
                "email": email if email is not None else None,
                "name": name if name is not None else None,
            }
            # Alternatively, to only include keys with non-None values:
            profile = {key: value for key, value in [("email", email), ("name", name)] if value is not None}
            return Response({"profile":profile,"parent_id":pid.id, "sheets": spreadsheet_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "Error accessing Google Sheets or Drive", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_user_info_from_google(creds):
    people_service = build('people', 'v1', credentials=creds)

    try:
        results = people_service.people().get(
            resourceName='people/me',
            personFields='names,emailAddresses'  # Request both name and email
        ).execute()

        name = None
        email = None

        names = results.get('names')
        if names:
            # Assuming the first name is the most relevant.  You can adjust this
            # to handle multiple names if needed (e.g., check for preferred names).
            name = names[0].get('displayName')

        email_addresses = results.get('emailAddresses')
        if email_addresses:
            # Usually, the primary email is the first one in the list, but check for isPrimary if needed.
            for email_data in email_addresses:
              if email_data.get('metadata', {}).get('primary'):
                email = email_data.get('value') # Returns the primary email address.
                break # Break if primary email found

            if not email: # If primary email not found, take the first email.
                email = email_addresses[0].get('value')
        
        return name, email
    except:
        return None, None
    
def sanitize_name(name):
    """Remove special characters and replace spaces with underscores"""
    import re
    # Replace special characters and spaces with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

class GoogleSpreadsheetDataView(APIView):
    @transaction.atomic()
    def get(self, request, token, parent_id, spreadsheet_id):
        tok1 = test_token(token)
        if tok1['status'] == 200:
            try:
                parent_id = parent_ids.objects.get(id=parent_id, parameter="google_sheets")
            except parent_ids.DoesNotExist:
                return Response({"error": "Authentication required"}, status=401)

            access_token = RefreshAccessToken.refresh(tok1['user_id'], "google_sheets", parent_id.table_id)
            if not access_token:
                return Response(ERROR_AUTH_REQUIRED, status=401)

            try:
                creds = Credentials(token=access_token)
                sheets_service = build("sheets", "v4", credentials=creds)

                spreadsheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheets = spreadsheet_metadata.get("sheets", [])
                spreadsheet_title = spreadsheet_metadata.get("properties", {}).get("title", "") or spreadsheet_id
                
                all_sheets_data = {}
                clickhouse_client = Clickhouse()
                sanitized_spreadsheet = sanitize_name(spreadsheet_title)

                # TokenStoring.objects.filter(id=parent_id.table_id).update(display_name=sanitized_spreadsheet,google_spreadsheet_id = spreadsheet_id)
                existing_names = TokenStoring.objects.filter(display_name__startswith=sanitized_spreadsheet).values_list("display_name", flat=True)
                
                # Extract numbers from existing display names
                existing_indices = []
                for name in existing_names:
                    match = re.search(rf"{sanitized_spreadsheet}_(\d+)$", name)
                    if match:
                        existing_indices.append(int(match.group(1)))

                # Determine the next available index
                next_index = max(existing_indices, default=0) + 1 if existing_indices else 1

                # Ensure uniqueness by appending the correct index
                sanitized_spreadsheet = f"{sanitized_spreadsheet}_{next_index}"
                
                # Update Display Name
                TokenStoring.objects.filter(id=parent_id.table_id).update(display_name=sanitized_spreadsheet,google_spreadsheet_id = spreadsheet_id)
                
                # Drop existing database if exists
                clickhouse_client.cursor.execute(text(f"DROP DATABASE IF EXISTS `{sanitized_spreadsheet}`"))
                
                # Create new database
                clickhouse_client.cursor.execute(text(f"CREATE DATABASE IF NOT EXISTS `{sanitized_spreadsheet}`"))

                for sheet in sheets:
                    sheet_name = sheet["properties"]["title"]
                    max_rows = sheet['properties'].get('gridProperties', {}).get('rowCount', 0)
                    max_cols = sheet['properties'].get('gridProperties', {}).get('columnCount', 0)
                    result = sheets_service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=f"{sheet_name}!1:{max_rows}"
                    ).execute()
                    
                    values = result.get("values", [])

                    # Skip empty nested lists and find the first non-empty row
                    non_empty_rows = [row for row in values if any(row)]  # Filter out empty lists
                    if not non_empty_rows:
                        continue  # Skip processing if there are no non-empty rows

                    # Take the first non-empty row as headers
                    headers_row = non_empty_rows[0]
                    data_rows = non_empty_rows[1:]  # Remaining rows as data

                    # Determine the maximum column length across all rows
                    max_columns = max(len(row) for row in non_empty_rows)

                    # Create headers based on the first valid row
                    headers = [str(col).strip() if idx < len(headers_row) and col else f"unnamed_{idx}" 
                            for idx, col in enumerate(headers_row[:max_columns] if len(headers_row) > max_columns else headers_row)]
                    
                    # Pad headers if the first row is shorter than the max column length
                    headers += [f"unnamed_{idx}" for idx in range(len(headers), max_columns)]
                    # Ensure unique headers
                    unique_headers = []
                    seen = set()
                    for idx, header in enumerate(headers):
                        if header in seen:
                            header = f"{header}_{idx}"
                        seen.add(header)
                        unique_headers.append(header)

                    # Process rows, ensuring uniform column count
                    cleaned_values = []
                    for row in data_rows:
                        padded_row = row + [''] * (len(unique_headers) - len(row))  # Pad missing columns
                        trimmed_row = padded_row[:len(unique_headers)]  # Trim extra columns
                        cleaned_values.append(trimmed_row)

                    try:
                        df = pd.DataFrame(cleaned_values, columns=unique_headers)
                        df = df.replace(r'^\s*$', np.nan, regex=True)  # Replace empty strings with NaN

                        # Store original column names to preserve all columns
                        all_columns = df.columns.tolist()

                        def convert_column_type(col):
                            """Convert column data types while ensuring all columns are retained."""
                            try:
                                # Try converting to numeric
                                numeric_col = pd.to_numeric(col, errors='coerce')
                                if numeric_col.notnull().all():  # If all values are valid, return
                                    return numeric_col

                                # Try converting to datetime
                                datetime_col = pd.to_datetime(col, errors='coerce')
                                if datetime_col.notnull().all():  # Ensure all values are valid dates
                                    return datetime_col

                                # If still object, check for boolean conversion
                                if col.dtype == object and col.apply(lambda x: isinstance(x, str)).all():
                                    boolean_map = {"true": True, "false": False, "yes": True, "no": False, "1": True, "0": False}
                                    if col.str.lower().isin(boolean_map.keys()).all():
                                        return col.str.lower().map(boolean_map)

                            except Exception:
                                pass
                            
                            return col.astype(str)  # If no conversion applied, return as-is

                        # Convert columns while keeping all original columns
                        for col in all_columns:
                            df[col] = convert_column_type(df[col])

                        # Ensure all original columns exist in final DataFrame
                        df = df.reindex(columns=all_columns, fill_value=np.nan)

                        # Create ClickHouse table with all columns
                        # table_columns = ", ".join([f"`{col.replace(' ', '_').replace('-', '_')}` String" for col in df.columns])
                        
                        sanitized_sheet = sanitize_name(sheet_name)
                        table_name = f"`{sanitized_spreadsheet}`.`{sanitized_sheet}`"
                        # Insert into ClickHouse
                        # table_name = f"`{spreadsheet_title}`.`{sheet_name.replace(' ', '_').replace('-', '_')}`"
                        insert_result = clickhouse.insert_df_into_clickhouse(table_name, df)
                        
                        if insert_result['status'] != 200:
                            print(f"Insert error for sheet {sheet_name}: {insert_result}")
                            return insert_result
                        
                        all_sheets_data[sheet_name] = result.get("values", [])
                    
                    except Exception as e:
                        print(f"Error processing sheet {sheet_name}: {str(e)}")
                        return Response({"error": f"Error processing sheet data {sheet_name}", "details": str(e)}, status=500)
                
                response_data = {
                    "status": 200,
                    "spreadsheet_id": spreadsheet_id,
                    "spreadsheet_title": spreadsheet_title,
                    "hierarchy_id": parent_id.id
                }
                
                return Response(response_data)
            except Exception as e:
                error_message = {"error": "Error processing spreadsheet data", "details": str(e)}
                return Response(error_message, status=500)
        return Response(tok1, status=tok1['status'])

def reinject_google_sheets_data(parameter, tok1, parent_id):
    """
    Reinject Google Sheets data by calling GoogleSpreadsheetDataView.get API
    
    Args:
        parameter (str): Parameter type (should be 'google_sheets')
        tok1 (dict): Token validation response containing user_id and status
        parent_id (int): Parent ID for the Google Sheets connection
    
    Returns:
        dict: API response from GoogleSpreadsheetDataView.get
    """
    try:
        # Get the TokenStoring entry using parent_id
        parent = parent_ids.objects.get(id=parent_id, parameter=parameter)
        token_entry = TokenStoring.objects.get(id=parent.table_id)
        
        # Get the stored spreadsheet ID
        spreadsheet_id = token_entry.google_spreadsheet_id
        if not spreadsheet_id:
            return {
                "status": 400,
                "error": "No spreadsheet ID found for this connection"
            }

        # Create request object with minimal required attributes
        request = type('Request', (), {'META': {}})()
        
        # Initialize GoogleSpreadsheetDataView
        view = GoogleSpreadsheetDataView()

        # tok1 = test_token(tok1.get('token', ''))
        up = UserProfile.objects.get(id=tok1['user_id'])
        token1 = AccessToken.objects.filter(user=up).latest('created').token
        
        # Call the get method
        response = view.get(
            request=request,
            token=token1,
            parent_id=parent_id,
            spreadsheet_id=spreadsheet_id
        )
        
        return {
            "status": 200,
            "data": response.data if hasattr(response, 'data') else None
        }
        
    except parent_ids.DoesNotExist:
        return {
            "status": 404,
            "error": "Parent ID not found"
        }
    except TokenStoring.DoesNotExist:
        return {
            "status": 404,
            "error": "Token entry not found"
        }
    except Exception as e:
        return {
            "status": 500,
            "error": f"Error reinjecting Google Sheets data: {str(e)}"
        }