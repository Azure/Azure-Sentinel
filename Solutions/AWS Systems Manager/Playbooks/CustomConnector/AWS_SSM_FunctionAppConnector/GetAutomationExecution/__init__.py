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

    # Get AutomationExecutionId from the request parameters
    automation_execution_id = req.params.get('AutomationExecutionId')

    if not automation_execution_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            automation_execution_id = req_body.get('AutomationExecutionId')

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
                logging.info('Calling function to get details of atuomation execution.')

                results = ssm_client.get_automation_execution(
                    AutomationExecutionId=automation_execution_id
                )
                #print(results)
                logging.info('Call to get details of atuomation execution is successful.')

                # Results returns ExecutionStartTime and ExecutionEndTime in datetime format, Convert to string.
                if results:
                    if results['AutomationExecution']['ExecutionStartTime']:
                        results['AutomationExecution']['ExecutionStartTime'] = results['AutomationExecution']['ExecutionStartTime'].strftime("%Y-%m-%dT%H:%M:%S%z")
                
                    if results['AutomationExecution']['ExecutionEndTime']:
                        results['AutomationExecution']['ExecutionEndTime'] = results['AutomationExecution']['ExecutionEndTime'].strftime("%Y-%m-%dT%H:%M:%S%z")
                
                    if results['AutomationExecution']['StepExecutions']:
                        for step in results['AutomationExecution']['StepExecutions']:
                            if step['ExecutionStartTime']:
                                step['ExecutionStartTime'] = step['ExecutionStartTime'].strftime("%Y-%m-%dT%H:%M:%S%z")
                        
                            if step['ExecutionEndTime']:
                                step['ExecutionEndTime'] = step['ExecutionEndTime'].strftime("%Y-%m-%dT%H:%M:%S%z")

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
                return func.HttpResponse(f"Automation Execution Not Found Exception", status_code=400)

        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass AutomationExecutionId parameters in the query string or request body.",
             status_code=400
        )
