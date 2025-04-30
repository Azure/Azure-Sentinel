import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DisableS3BucketPublicAccess function processed a request.')
    
    ## Get the name of the bucket from the request parameters or body
    bucket_name = req.params.get('BucketName')
    
    if not bucket_name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            bucket_name = req_body.get('BucketName')

    if bucket_name:
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.environ["AWS_AccessKeyId"],
                aws_secret_access_key=os.environ["AWS_SecretAccessKey"],
            )
            try:
                ## Define the public access block configuration
                public_access_block_config = {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                } 
                ## Disable public access to the bucket
                response = s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration=public_access_block_config
                )
            except s3_client.exceptions.NoSuchBucket as err:
                return func.HttpResponse(f'S3 Bucket {bucket_name} does not exist.', status_code=404)
            except s3_client.exceptions.InvalidBucketName as err:
                return func.HttpResponse(f'Invalid bucket name: {bucket_name}.', status_code=400)

            return func.HttpResponse(json.dumps(response), status_code=200)
        except ClientError as err:
            return func.HttpResponse(str(err), status_code=401)
    else:
        return func.HttpResponse(
            "Please pass a BucketName parameter in the url.", status_code=400
        )