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

    # Get AutomationExecutionId and Type from the request parameters
    automation_execution_id = req.params.get('AutomationExecutionId')
    type = req.params.get('Type')

    if not (automation_execution_id and type):
        try:
            req_body = json.loads(req.get_json())
        except ValueError:
            pass
        else:
            automation_execution_id = req_body.get('AutomationExecutionId')
            type = req_body.get('Type')

    # Set parameter dictionary based on the provided request parameters
    kwargs = {}
    if automation_execution_id:
        kwargs['AutomationExecutionId'] = automation_execution_id
    if type:
        kwargs['Type'] = type

    if automation_execution_id:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function to stop atuomation execution.')

                results = ssm_client.stop_automation_execution(**kwargs)
                
                logging.info('Call to stop automation execution successful.')

                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
            
            except ssm_client.exceptions.InternalServerError as ex:
                logging.error(f"Internal Server Exception: {str(ex)}")
                return func.HttpResponse("Internal Server Exception", status_code=500)

            except ssm_client.exceptions.AutomationExecutionNotFoundException as ex:
                logging.error(f"Automation Execution Not Found Exception: {str(ex)}")
                return func.HttpResponse("Automation Execution Not Found Exception", status_code=400)

            except ssm_client.exceptions.InvalidAutomationStatusUpdateException as ex:
                logging.error(f"Invalid Automation Status Update Exception: {str(ex)}")
                return func.HttpResponse("Invalid Automation Status Update Exception", status_code=400)
        
        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass AutomationExecutionId and Type(optional) parameters in the query string or request body.",
             status_code=400
        )
