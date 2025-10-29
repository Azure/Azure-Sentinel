
import boto3
import json
import csv
import time
import pandas as pd
from datetime import datetime
import os

logs = boto3.client('logs')
s3 = boto3.resource('s3')


# Please set the following parameters:
LOG_GROUP_NAME = os.environ['LOG_GROUP_NAME'] # Please enter log group name
LOG_STREAM_PREFIX = os.environ['LOG_STREAM_PREFIX'] # Please enter log stream prefix
BUCKET_NAME = os.environ['BUCKET_NAME'] # Please enter bucket name
BUCKET_PREFIX = os.environ['BUCKET_PREFIX'] # Please enter bucket prefix that ends with '/' , if no such, leave empty
OUTPUT_FILE_NAME = os.environ['OUTPUT_FILE_NAME'] # Please change to desired name
START_TIME_UTC = datetime.strptime(os.environ['START_TIME_UTC'], '%m/%d/%Y %H:%M') # Please enter start time for exporting logs in the following format: '%m/%d/%Y %H:%M' for example: '12/31/2022 06:55'  pay attention to time differences, here it should be UTC time
END_TIME_UTC = datetime.strptime(os.environ['END_TIME_UTC'], '%m/%d/%Y %H:%M') # Please enter end time for exporting logs in the following format: '%m/%d/%Y %H:%M' for example: '12/31/2022 07:10' pay attention to time differences, here it should be UTC time

def lambda_handler(event, context):
    """
    The function gets data from cloud watch and put it in the desired bucket in the required format for Sentinel.
    :param event: object that contains information about the current state of the execution environment.
    :param context: object that contains information about the current execution context.
    """
    unix_start_time = int(time.mktime(START_TIME_UTC.timetuple()))*1000
    unix_end_time = int(time.mktime(END_TIME_UTC.timetuple()))*1000
    try:
        # Get log streams that match the prefix
        log_streams_response = logs.describe_log_streams(
            logGroupName=LOG_GROUP_NAME,
            logStreamNamePrefix=LOG_STREAM_PREFIX  # Use the prefix for the log stream
        )

        # Iterate over the log streams and fetch log events for each
        for log_stream in log_streams_response['logStreams']:
            log_stream_name = log_stream['logStreamName']
            
            # Gets objects from cloud watch
            response = logs.get_log_events(
                logGroupName=LOG_GROUP_NAME,
                logStreamName=log_stream_name,
                startTime=unix_start_time,
                endTime=unix_end_time,
            )
            
            # Convert events to json object
            json_string = json.dumps(response)
            json_object = json.loads(json_string)
            
            df = pd.DataFrame(json_object['events'])
            print(unix_start_time)
            if df.empty:
                print('No events for specified time in the log stream', log_stream_name)
                continue
            
            # Convert unix time to zulu time for example from 1671086934783 to 2022-12-15T06:48:54.783Z
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]+'Z'
            
            # Remove unnecessary column
            fileToS3 = df.drop(columns=["ingestionTime"])
            
            sanitized_stream_name = log_stream_name.replace('/', '_')
            
            # Export data to temporary file in the right format, which will be deleted as soon as the session ends
            fileToS3.to_csv( f'/tmp/{OUTPUT_FILE_NAME}_{sanitized_stream_name}.gz', index=False, header=False, compression='gzip', sep = ' ', escapechar=' ',  doublequote=False, quoting=csv.QUOTE_NONE)
            
            # Upload data to desired folder in bucket
            s3.Bucket(BUCKET_NAME).upload_file(f'/tmp/{OUTPUT_FILE_NAME}_{sanitized_stream_name}.gz', f'{BUCKET_PREFIX}{OUTPUT_FILE_NAME}_{sanitized_stream_name}.gz')
            

    except Exception as e:
        print("    Error exporting %s: %s" % (LOG_GROUP_NAME, getattr(e, 'message', repr(e))))