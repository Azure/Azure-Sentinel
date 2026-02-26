import logging
from unittest import result
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
                # Get the query results for an executed query
                logging.info(f'Sending Query Request.')
                response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
                results = response['ResultSet']['Rows']
                
                # Format the result in json 
                headers = []
                rows = []
                is_header_row = True

                for row in results:
                    tmp_row = []
                    for data in row['Data']:
                        tmp_row.append(list(dict(data).values())[0])

                    if is_header_row:
                        headers = tmp_row
                        is_header_row = False
                    else:
                        rows.append(tmp_row)
                
                json_result = []

                for col in rows:
                    result_col = dict(zip(headers, col))          
                    json_result.append(result_col)

                # Return the formatted response
                return func.HttpResponse(
                    json.dumps(json_result),
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
