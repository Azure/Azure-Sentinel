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

    # Get Filters, Aggregators, ResultAttributes, NextToken and MaxResults from the request parameters
    filters = req.params.get('Filters')
    aggregators = req.params.get('Aggregators')
    result_attributes = req.params.get('ResultAttributes')
    next_token = req.params.get('NextToken')
    max_results = req.params.get('MaxResults')

    if not (filters and aggregators and result_attributes and next_token and max_results):
        try:
            req_body = json.loads(req.get_json())
        except ValueError:
            pass
        else:
            filters = req_body.get('Filters')
            aggregators = req_body.get('Aggregators')
            result_attributes = req_body.get('ResultAttributes')
            next_token = req_body.get('NextToken')
            max_results = req_body.get('MaxResults')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if filters:
        kwargs['Name'] = filters
    if aggregators:
        kwargs['VersionName'] = aggregators
    if result_attributes:
        kwargs['DocumentVersion'] = result_attributes
    if next_token:
        kwargs['DocumentFormat'] = next_token
    if max_results:
        kwargs['MaxResults'] = max_results

    try:
        logging.info('Creating Boto3 SSM Client.')
        ssm_client = boto3.client(
            "ssm",
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
        )

        try:
            logging.info('Calling function to get AWS SSM Inventory.')

            results = ssm_client.get_inventory(**kwargs)

            logging.info('Call to get AWS SSM Inventory successful.')

            # Return the results
            return func.HttpResponse(
                json.dumps(results),
                headers = {"Content-Type": "application/json"},
                status_code = 200
            )
            
        except ssm_client.exceptions.InternalServerError as ex:
            logging.error(f"Internal Server Exception: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)

        except ssm_client.exceptions.InvalidFilter as ex:
            logging.error(f"Invalid Filter Exception: {str(ex)}")
            return func.HttpResponse("Invalid Filter Exception", status_code=400)

        except ssm_client.exceptions.InvalidInventoryGroupException as ex:
            logging.error(f"Invalid Inventory Group Exception: {str(ex)}")
            return func.HttpResponse("Invalid Inventory Group Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidNextToken as ex:
            logging.error(f"Invalid NextToken Exception: {str(ex)}")
            return func.HttpResponse("Invalid NextToken Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidDocumentVersion as ex:
            logging.error(f"Invalid Invalid TypeName Exception: {str(ex)}")
            return func.HttpResponse("Invalid TypeName Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidDocumentVersion as ex:
            logging.error(f"Invalid Aggregator Exception: {str(ex)}")
            return func.HttpResponse("Invalid Aggregator Exception", status_code=400)
        
        except ssm_client.exceptions.InvalidDocumentVersion as ex:
            logging.error(f"Invalid ResultAttribute Exception: {str(ex)}")
            return func.HttpResponse("Invalid ResultAttribute Exception", status_code=400)
        
            
    except ClientError as ex:
        logging.error(f"SSM Client Error: {str(ex)}")
        return func.HttpResponse("SSM Client Error", status_code=401)
        
    except Exception as ex:
        logging.error(f"Exception Occured: {str(ex)}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
