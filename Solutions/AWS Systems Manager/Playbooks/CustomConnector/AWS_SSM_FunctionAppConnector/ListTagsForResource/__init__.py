import logging
import boto3
import json
import azure.functions as func
from os import environ
from botocore.exceptions import ClientError


def main(req: func.HttpRequest) -> func.HttpResponse:
    '''
    Returns the result of AWS API call.

        Parameters:
            req (HttpRequest): Request Parameters
        Returns:
            func.HttpResponse
    '''
    logging.info(f'Resource Requested: {func.HttpRequest}')

    # Get AWS ID and Key
    try:
        aws_access_key_id = environ['AWSAccessKeyID']
        aws_secret_access_key = environ['AWSSecretAccessKey']
        aws_region_name = environ['AWSRegionName']

    except KeyError as ke:
        logging.error(f'Invalid Settings. {ke.args} configuration is missing.')
        return func.HttpResponse(
             'Invalid Settings. AWS Access ID/Key configuration is missing.',
             status_code=500
        )
    
    # Get ResourceType and ResourceId from the request parameters
    resource_type = req.params.get('ResourceType')
    resource_id = req.params.get('ResourceId')

    if not (resource_type and resource_id):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            resource_type = req_body.get('ResourceType')
            resource_id = req_body.get('ResourceId')

    if resource_type and resource_id:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function to list tags of a resource.')

                results = ssm_client.list_tags_for_resource(
                    ResourceType=resource_type,
                    ResourceId=resource_id
                )

                logging.info('Call to list tags of a resource completed.')
                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
            
            except ssm_client.exceptions.InternalServerError as ex:
                logging.error(f"Internal Server Exception: {str(ex)}")
                return func.HttpResponse("Internal Server Exception", status_code=500)

            except ssm_client.exceptions.InvalidResourceType as ex:
                logging.error(f"Invalid Resourse Type Exception: {str(ex)}")
                return func.HttpResponse(f"Resourse Type Exception", status_code=400)

            except ssm_client.exceptions.InvalidResourceId as ex:
                logging.error(f"Invalid Resourse ID Exception: {str(ex)}")
                return func.HttpResponse("Invalid Resourse ID Exception", status_code=400)
            
        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass ResourceType and ResourceId in the query string or request body.",
             status_code=400
        )
