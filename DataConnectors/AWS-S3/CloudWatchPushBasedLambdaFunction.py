import boto3
import json
import csv
import pandas as pd
import os
import base64
import gzip
from datetime import datetime

logs = boto3.client('logs')
s3 = boto3.resource('s3')

# Parameters
LOG_STREAM_PREFIX = os.environ['LOG_STREAM_PREFIX']  # Log stream prefix to filter
BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PREFIX = os.environ['BUCKET_PREFIX']
OUTPUT_FILE_NAME = os.environ.get('OUTPUT_FILE_NAME', '')  # Default to an empty string if not set

def lambda_handler(event, context):
    """
    Processes incoming compressed and encoded log events, filtering by log stream prefix,
    and uploads them to S3 in the required format.
    """
    try:
        # Decode and decompress the CloudWatch log data
        encoded_zipped_data = event['awslogs']['data']
        zipped_data = base64.b64decode(encoded_zipped_data)
        data = gzip.decompress(zipped_data)
       
        # Convert the decompressed data from JSON format
        log_data = json.loads(data)
       
        # Check if the log stream name starts with the specified prefix
        if not log_data['logStream'].startswith(LOG_STREAM_PREFIX):
            print(f"Skipping log stream {log_data['logStream']} as it doesn't match the prefix.")
            return
 
        # Convert log events to a DataFrame for processing
        df = pd.DataFrame(log_data['logEvents'])
 
        if df.empty:
            print('No events to process.')
            return
 
        # Convert timestamps to Zulu format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]+'Z'
 
        # Check if 'ingestionTime' exists before dropping
        if 'ingestionTime' in df.columns:
            fileToS3 = df.drop(columns=["ingestionTime", "id"])
        elif 'timestamp' in df.columns:
            fileToS3 = df.drop(columns=["timestamp", "id"])
        else:
            fileToS3 = df.drop(columns=["id"])  # Use the DataFrame as is if 'ingestionTime' doesn't exist
 
        # Prepare date-based folder structure
        current_date = datetime.utcnow().strftime('%Y/%m/%d')  # Format as YYYY/MM/DD
        sanitized_stream_name = log_data['logStream'].replace('/', '_')
        first_timestamp = df['timestamp'].iloc[0]
        file_path = f'/tmp/{sanitized_stream_name}_{first_timestamp}.gz'
        fileToS3.to_csv(file_path, index=False, header=False, compression='gzip', sep=' ', escapechar=' ', doublequote=False, quoting=csv.QUOTE_NONE)
 
        # Update S3 path with or without OUTPUT_FILE_NAME
        s3_key = f'{BUCKET_PREFIX}{current_date}/'
        if OUTPUT_FILE_NAME:  # Add OUTPUT_FILE_NAME if it's set
            s3_key += f'{OUTPUT_FILE_NAME}/'
        s3_key += f'{sanitized_stream_name}/{first_timestamp}.gz'
 
        # Upload to S3
        s3.Bucket(BUCKET_NAME).upload_file(file_path, s3_key)
        print(f'Uploaded logs to S3: {s3_key}')
 
    except Exception as e:
        print("Error exporting logs:", repr(e))
