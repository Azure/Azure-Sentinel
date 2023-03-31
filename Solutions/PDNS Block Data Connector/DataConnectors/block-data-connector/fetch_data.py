import os
from datetime import datetime, timedelta, timezone
import json
import logging
from typing import Any, Dict, List, Tuple
import boto3
from .state_manager import StateManager


StixEvent = Dict[str, Any]

DATE_FORMAT = "%Y-%m-%d-%H"
FILE_SHARE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']

def inclusive_datetime_range(start_datetime, end_datetime):
        start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0)
        end_datetime = end_datetime.replace(minute=0, second=0, microsecond=0)
        for n in range(int((end_datetime - start_datetime).total_seconds()) // 3600 + 1):
            yield start_datetime + timedelta(hours=n)

class AWSDataFetcher:

    def __init__(self, bucket_arn : str, region_name : str, client_prefix : str, key_id : str, secret_key : str):
        self.s3_client = boto3.client(
                "s3",
                region_name=region_name,
                aws_access_key_id=key_id,
                aws_secret_access_key=secret_key
            )
        self.state_manager = StateManager(FILE_SHARE_CONNECTION_STRING)
        self.bucket_arn = bucket_arn
        self.client_prefix = client_prefix

    def get_recent_file_keys_and_dates(self) -> List[Tuple[str, str]]:
        checkpoint_string = self.state_manager.get()
        checkpoint = json.loads(checkpoint_string) if checkpoint_string else {"Key": "", "Date": ""}

        last_key_read = checkpoint['Key'] if 'Key' in checkpoint else ""
        last_date_read = checkpoint['Date'] if 'Date' in checkpoint else ""

        utc_now = datetime.now(timezone.utc)
        utc_last_read = datetime.fromisoformat(last_date_read) if last_date_read else utc_now - timedelta(hours=6)

        if (utc_now - utc_last_read).total_seconds() > 21600:
            utc_last_read = utc_now - timedelta(hours=6)

        keys_and_dates = []
        for datetime_to_hour in inclusive_datetime_range(utc_last_read, utc_now):
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_arn,
                Prefix=f"{self.client_prefix}/blocks-{datetime_to_hour.strftime(DATE_FORMAT)}",
                StartAfter=last_key_read
            )
            if 'Contents' in response: 
                keys_and_dates += [(file_object['Key'], file_object['LastModified']) for file_object in response['Contents']]            

        return keys_and_dates

    
    def get_stix_events_from_file_key(self, key: str) -> List[StixEvent]:
        s3_object = self.s3_client.get_object(Bucket=self.bucket_arn, Key=key)['Body']

        file_content = s3_object.read()
        s3_object.close()

        try:
            json_content = json.loads(file_content)
        except Exception as e:
            logging.error(
                'Expected file to contain valid json, but was unable to parse.')
            raise e

        if not (json_content['payload'] and json_content['payload']['objects']):
            raise Exception(
                "Expected to find STIX events at path '$.payload.objects',"
                "but no such path existed."
            )

        return json_content['payload']['objects']