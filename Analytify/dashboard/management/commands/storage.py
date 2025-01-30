import io
import boto3
from PIL import Image
import datetime
import json
import os
from project import settings

try:
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
except Exception as e:
    print(e)


def create_s3_file(input_file_path, sheet_ids_list, hierarchy_id, querysetid, bucket_name):
    """
        Creates a new file in S3 with the provided data.
        
        Args:
            input_file_path (str): The path to the input JSON text file.
            sheet_ids_list (list): The list of sheet IDs.
            server_id (int): The server ID.
            querysetid (object): The queryset ID object.
            bucket_name (str): The name of the S3 bucket where the file will be stored.
            
        Returns:
            str: The URL of the created file.
        """
    # Read the JSON data from the .txt file
    with open(input_file_path, 'r') as txt_file:
        data = json.load(txt_file)

    # Update the sheetId in the data
    for index, item in enumerate(data):
        item['sheetId'] = sheet_ids_list[index]
        item['databaseId'] = hierarchy_id
        item['qrySetId'] = querysetid.queryset_id

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
    output_file_name = f"data_{current_datetime}.txt"
    
    if settings.file_save_path == 's3':
        output_file_key = f'insightapps/dashboard/{output_file_name}'
        json_data = json.dumps(data, indent=4)
        file_buffer = io.BytesIO(json_data.encode('utf-8'))
        s3.upload_fileobj(file_buffer, Bucket=bucket_name, Key=output_file_key)
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{output_file_key}"
    else:
        # Local storage
        media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'dashboard')
        os.makedirs(media_path, exist_ok=True)
        output_file_key = os.path.join('insightapps', 'dashboard', output_file_name)
        local_path = os.path.join(settings.MEDIA_ROOT, output_file_key)
        
        with open(local_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        file_url = f"{settings.file_save_url.rstrip('/')}/media/{output_file_key}"
    
    return file_url, output_file_key

def create_s3_image(image_file_path, current_datetime, bucket_name):
    
    """
    Creates a new image in S3 with the provided image file.
    
    Args:
        image_file_path (str): The path to the input image file.
        current_datetime (str): The current date and time.
        bucket_name (str): The name of the S3 bucket where the image will be stored.
        
    Returns:
        str: The URL of the created image.
    """

    image = Image.open(image_file_path)
    output_image_name = f"employee_image_{current_datetime}.jpeg"
    
    if settings.file_save_path == 's3':
        output_image_key = f'insightapps/dashboard/images/{output_image_name}'
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        s3.upload_fileobj(image_buffer, Bucket=bucket_name, Key=output_image_key)
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{output_image_key}"
    else:
        # Local storage
        media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'dashboard', 'images')
        os.makedirs(media_path, exist_ok=True)
        output_image_key = os.path.join('insightapps', 'dashboard', 'images', output_image_name)
        local_path = os.path.join(settings.MEDIA_ROOT, output_image_key)
        
        image.save(local_path, format='PNG')
        image_url = f"{settings.file_save_url.rstrip('/')}/media/{output_image_key}"
    
    return image_url, output_image_key

def upload_sheetdata_file_to_s3(input_file_path, bucket_name, sheetfilter_queryset_id):
    with open(input_file_path, 'r') as txt_file:
        data = json.load(txt_file)

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
    output_file_name = f"sheetdata_{sheetfilter_queryset_id}_{current_datetime}.txt"
    
    if settings.file_save_path == 's3':
        output_file_key = f'insightapps/sheetdata/{output_file_name}'
        json_data = json.dumps(data, indent=4)
        file_buffer = io.BytesIO(json_data.encode('utf-8'))
        s3.upload_fileobj(file_buffer, Bucket=bucket_name, Key=output_file_key)
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{output_file_key}"
    else:
        # Local storage
        media_path = os.path.join(settings.MEDIA_ROOT, 'insightapps', 'sheetdata')
        os.makedirs(media_path, exist_ok=True)
        output_file_key = os.path.join('insightapps', 'sheetdata', output_file_name)
        local_path = os.path.join(settings.MEDIA_ROOT, output_file_key)
        
        with open(local_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        file_url = f"{settings.file_save_url.rstrip('/')}/media/{output_file_key}"
    
    return file_url, output_file_key