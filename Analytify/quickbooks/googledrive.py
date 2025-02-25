from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as rf_status
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from quickbooks.models import TokenStoring
from dashboard.views import test_token
import io
from project import settings

class GoogleDriveListFilesView(APIView):
    def get(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])
        
        try:
            # Get stored credentials
            stored_token = TokenStoring.objects.get(user=tok1['user_id'], parameter="google_sheets")
            credentials = Credentials(
                token=stored_token.accesstoken,
                refresh_token=stored_token.refreshtoken,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )

            # Build the Drive service
            service = build('drive', 'v3', credentials=credentials)

            # List files
            # List files with correct query format
            results = service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet' or mimeType='text/csv'",
                pageSize=30,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)",
            ).execute()

            
            files = results.get('files', [])
            return Response({
                "files": files
            }, status=rf_status.HTTP_200_OK)

        except TokenStoring.DoesNotExist:
            return Response({"error": "Authentication required"}, status=rf_status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=rf_status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleDriveFileDetailsView(APIView):
    def get(self, request, token, file_id):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])
        
        try:
            stored_token = TokenStoring.objects.get(user=tok1['user_id'], parameter="google_sheets")
            credentials = Credentials(
                token=stored_token.accesstoken,
                refresh_token=stored_token.refreshtoken,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )

            service = build('drive', 'v3', credentials=credentials)
            
            # Get file metadata
            file = service.files().get(fileId=file_id, fields='id, name, mimeType, createdTime, modifiedTime, size, parents').execute()
            
            return Response(file, status=rf_status.HTTP_200_OK)

        except TokenStoring.DoesNotExist:
            return Response({"error": "Authentication required"}, status=rf_status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=rf_status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleDriveSearchView(APIView):
    def get(self, request, token):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])
        
        query = request.GET.get('q', '')
        
        try:
            stored_token = TokenStoring.objects.get(user=tok1['user_id'], parameter="google_sheets")
            credentials = Credentials(
                token=stored_token.accesstoken,
                refresh_token=stored_token.refreshtoken,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )

            service = build('drive', 'v3', credentials=credentials)
            
            # Search for files
            results = service.files().list(
                q=f"name contains '{query}' and (mimeType = 'application/vnd.google-apps.spreadsheet' or mimeType = 'text/csv')",
                # q=f"name contains '{query}'",
                pageSize=30,
                fields="files(id, name, mimeType, createdTime, modifiedTime, size)"
            ).execute()
            
            files = results.get('files', [])
            return Response({
                "files": files
            }, status=rf_status.HTTP_200_OK)

        except TokenStoring.DoesNotExist:
            return Response({"error": "Authentication required"}, status=rf_status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=rf_status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleDriveDownloadView(APIView):
    def get(self, request, token, file_id,range):
        tok1 = test_token(token)
        if tok1['status'] != 200:
            return Response(tok1, status=tok1['status'])
        
        try:
            stored_token = TokenStoring.objects.get(user=tok1['user_id'], parameter="google_sheets")
            credentials = Credentials(
                token=stored_token.accesstoken,
                refresh_token=stored_token.refreshtoken,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )

            drive_service = build('drive', 'v3', credentials=credentials)
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Get file metadata first
            file_metadata = drive_service.files().get(fileId=file_id, fields='id, name, mimeType').execute()
            mime_type = file_metadata.get('mimeType', '')

            if mime_type not in ['application/vnd.google-apps.spreadsheet', 'text/csv']:
                return Response({
                    "error": "Only CSV and Excel files can be downloaded"
                }, status=rf_status.HTTP_400_BAD_REQUEST)
                        
            file_content = None
            
            # Handle different types of files
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                # Handle Google Sheets
                result = sheets_service.spreadsheets().values().get(
                    spreadsheetId=file_id,
                    range=range  # Fetch a large range to get all data
                ).execute()
                file_content = result.get('values', [])
                
            # elif mime_type == 'application/vnd.google-apps.document':
            #     # Handle Google Docs
            #     docs_service = build('docs', 'v1', credentials=credentials)
            #     document = docs_service.documents().get(documentId=file_id).execute()
                
            #     # Extract text content from the document
            #     content = []
            #     for elem in document.get('body', {}).get('content', []):
            #         if 'paragraph' in elem:
            #             paragraph_text = ''
            #             for text_run in elem['paragraph'].get('elements', []):
            #                 if 'textRun' in text_run:
            #                     paragraph_text += text_run['textRun'].get('content', '')
            #             if paragraph_text.strip():
            #                 content.append(paragraph_text.strip())
            #     file_content = content
            elif mime_type == 'text/csv':
                # Handle CSV
                request = drive_service.files().get_media(fileId=file_id)
                file_handle = io.BytesIO()
                downloader = MediaIoBaseDownload(file_handle, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                
                file_handle.seek(0)
                content = file_handle.read().decode('utf-8')
                file_content = content.splitlines()
            # else:
            #     # For text-based files, try to get the content directly
            #     try:
            #         request = drive_service.files().get_media(fileId=file_id)
            #         file_handle = io.BytesIO()
            #         downloader = MediaIoBaseDownload(file_handle, request)
            #         done = False
            #         while not done:
            #             _, done = downloader.next_chunk()
                    
            #         file_handle.seek(0)
            #         content = file_handle.read().decode('utf-8')
            #         file_content = content.splitlines()
                # except:
                #     return Response({
                #         "error": "This file type is not supported for content viewing. Only text-based files, Google Docs, and Google Sheets can be viewed."
                #     }, status=rf_status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "file_name": file_metadata['name'],
                "mime_type": mime_type,
                "content": file_content
            }, status=rf_status.HTTP_200_OK)

        except TokenStoring.DoesNotExist:
            return Response({"error": "Authentication required"}, status=rf_status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=rf_status.HTTP_500_INTERNAL_SERVER_ERROR)