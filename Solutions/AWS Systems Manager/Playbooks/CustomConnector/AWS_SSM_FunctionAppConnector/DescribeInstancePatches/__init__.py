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

    # Get InstanceId, Filters, MaxResults and NextToken from the request parameters
    instanceid = req.params.get('InstanceId')
    filters = req.params.get('Filters')
    max_results = req.params.get('MaxResults')
    next_token = req.params.get('NextToken')

    if not (instanceid or filters or max_results or next_token):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            instanceid = req_body.get('InstanceId')
            filters = req_body.get('Filters')
            max_results = req_body.get('MaxResults')
            next_token = req_body.get('NextToken')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if instanceid:
        kwargs['InstanceId'] = instanceid
    if filters:
        kwargs['Filters'] = filters
    if max_results:
        kwargs['MaxResults'] = max_results
    if next_token:
        kwargs['NextToken'] = next_token

    if instanceid:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function describe_instance_patches.')

                results = ssm_client.describe_instance_patches(**kwargs)

                logging.info('Call to function describe_instance_patches successful.')

                # Result returns InstalledTime as datetime.datetime object which is not JSON serializable. Convert datetime.datetime object to string.
                if results and ('Patches' in results):
                    for patch in results['Patches']:
                        if 'InstalledTime' in patch:
                            patch['InstalledTime'] = patch['InstalledTime'].strftime("%Y-%m-%d %H:%M:%S") 

                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )

            except ssm_client.exceptions.InternalServerError as ex:
                logging.error(f"Internal Server Exception: {str(ex)}")
                return func.HttpResponse("Internal Server Exception", status_code=500)

            except ssm_client.exceptions.InvalidInstanceId as ex:
                logging.error(f"Invalid InstanceId Exception: {str(ex)}")
                return func.HttpResponse("Invalid InstanceId Exception", status_code=400)

            except ssm_client.exceptions.InvalidNextToken as ex:
                logging.error(f"Invalid NextToken Exception: {str(ex)}")
                return func.HttpResponse("Invalid NextToken Exception", status_code=400)

            except ssm_client.exceptions.InvalidFilter as ex:
                logging.error(f"Invalid Filter Exception: {str(ex)}")
                return func.HttpResponse("Invalid Filter Exception", status_code=400)


        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)

        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
    else:
        return func.HttpResponse(
             "Pass InstanceId (required) and (optional) Filters, NextToken, MaxResults parameter(s) in the query string or request body.",
             status_code=400
        )