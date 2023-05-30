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

    # Get Filters, MaxResults and NextToken from the request parameters
    filters = req.params.get('Filters')
    max_results = req.params.get('MaxResults')
    next_token = req.params.get('NextToken')

    if not (filters and max_results and next_token):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            filters = req_body.get('Filters')
            max_results = req_body.get('MaxResults')
            next_token = req_body.get('NextToken')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if filters:
        kwargs['Filters'] = json.loads(filters)
    if max_results:
        kwargs['MaxResults'] = int(max_results)
    if next_token:
         kwargs['NextToken'] = next_token

    try:
        logging.info('Creating Boto3 SSM Client.')
        ssm_client = boto3.client(
            "ssm",
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
        )
        try:
            logging.info('Calling function to list AWS SSM Documents.')
            
            results = ssm_client.list_documents(**kwargs)

            logging.info('ListDocuments API call successful.')

            # Result returns CreatedDate as datetime object. Convert datetime to string
            if results and 'DocumentIdentifiers' in results and results['DocumentIdentifiers'] is not None:
                for result in results['DocumentIdentifiers']:
                    result['CreatedDate'] = result['CreatedDate'].strftime("%Y-%m-%dT%H:%M:%S%z")

            logging.info('Datetime object converted to string.')
            
            # Return the results
            return func.HttpResponse(
                  json.dumps(results, skipkeys=True),
                  headers = {"Content-Type": "application/json"},
                  status_code = 200
              )

        except ssm_client.exceptions.InternalServerError as ex:
              logging.error(f"Internal Server Exception: {str(ex)}")
              return func.HttpResponse("Internal Server Exception", status_code=500)
        except ssm_client.exceptions.InvalidFilterKey as ex:
              logging.error(f"Invalid Filter Key Exception: {str(ex)}")
              return func.HttpResponse(f"Invalid Filter Key Exception", status_code=400)
        except ssm_client.exceptions.InvalidNextToken as ex:
              logging.error(f"Invalid Next Token Exception: {str(ex)}")
              return func.HttpResponse("Invalid Next Token Exception", status_code=400)

    except ClientError as ex:
          logging.error(f"SSM Client Error: {str(ex)}")
          return func.HttpResponse("SSM Client Error", status_code=401)

    except Exception as ex:
          logging.error(f"Exception Occured: {str(ex)}")
          return func.HttpResponse("Internal Server Exception", status_code=500)
