
import boto3
import json
import csv
import time
import pandas as pd
from datetime import datetime

logs = boto3.client('logs')
s3 = boto3.resource('s3')


# Please set the following parameters:
log_group_name = "" # Please enter log group name
log_stream_name = "" # Please enter log stream name
bucket_name = "" # Please enter bucket name
bucket_prefix = "" # Please enter bucket prefix that ends with '/' , if no such, leave empty
output_file_name = "" # Please change to desired name
start_time = datetime(2022,12,15,6,40) # Please enter start time for exporting logs (year, month, day, hour, minutes) pay attention to time differences, here it should be UTC time
end_time = datetime(2022,12,15,6,58) # Please enter end time for exporting logs (year, month, day, hour, minutes) pay attention to time differences, here it should be UTC time

def lambda_handler(event, context):
    unix_start_time = int(time.mktime(start_time.timetuple()))*1000
    unix_end_time = int(time.mktime(end_time.timetuple()))*1000
    try:
        # Gets objects from cloud watch
        response = logs.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startTime=unix_start_time,
            endTime=unix_end_time,
        )
        
        # Convert events to json object
        json_string = json.dumps(response)
        json_object = json.loads(json_string)
        
        df = pd.DataFrame(json_object['events'])
        if df.empty:
            print('No events for specified time')
            return
        
        # Convert unix time to zulu time
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3]+'Z'
        
        # Remove unnecessary column
        fileToS3 = df.drop(columns=["ingestionTime"])

        # Export data to temporary file in the right format, which will be deleted as soon as the session ends
        fileToS3.to_csv('/tmp/'+output_file_name+'.gz', index=False, header=False, compression='gzip', sep = ' ', escapechar=' ',  doublequote=False, quoting=csv.QUOTE_NONE)
        
        # Upload data to desired folder in bucket
        s3.Bucket(bucket_name).upload_file('/tmp/'+output_file_name+'.gz', bucket_prefix+output_file_name+'.gz')

    except Exception as e:
        print("    Error exporting %s: %s" % (log_group_name, getattr(e, 'message', repr(e))))


