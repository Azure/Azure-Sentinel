import logging
import boto3
import json
import azure.functions as func
from botocore.exceptions import ClientError
from os import environ


def main(req: func.HttpRequest) -> func.HttpResponse:
    
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

    # Get Query Execution Id from the request parameter
    query_execution_id = req.params.get('QueryExecutionId')

    if not query_execution_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            query_execution_id = req_body.get('QueryExecutionId')

    if query_execution_id:
        
        try:
            logging.info(f'Creating Boto3 Athena Client.')
            athena_client = boto3.client(
                "athena",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )
            
            try:
                # Get the query execution details for a query
                logging.info(f'Sending request.')
                response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
                results = response['QueryExecution']['Status']['State']
                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
        
            except athena_client.exceptions.InternalServerException as ex:
                logging.error(f"Internal Server Error: {str(ex)}")
                return func.HttpResponse("Internal Server Error", status_code=404)

            except athena_client.exceptions.InvalidRequestException as ex:
                logging.error(f"Invalid Request Exception: {str(ex)}")
                return func.HttpResponse("Invalid Request Exception: Not a valid QueryExecutionId", status_code=400)

        except ClientError as ex:
            logging.error(f"Athena Client Error: {str(ex)}")
            return func.HttpResponse("Athena Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)

    else:
        return func.HttpResponse(
             "Please pass QueryExecutionId in the query string.",
             status_code=400
        )
