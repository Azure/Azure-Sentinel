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

    # Get all the parameters from the request
    document_name = req.params.get('DocumentName')
    document_version = req.params.get('DocumentVersion')
    parameters = req.params.get('Parameters')
    client_token = req.params.get('ClientToken')
    mode = req.params.get('Mode')
    target_account = req.params.get('TargetAccount')
    targets = req.params.get('Targets')
    target_maps = req.params.get('TargetMaps')
    max_concurrency = req.params.get('MaxConcurrency')
    max_errors = req.params.get('MaxErrors')
    target_locations = req.params.get('TargetLocations')
    tags = req.params.get('Tags')
    alarm_configuration = req.params.get('AlarmConfiguration')

    if not (document_name and document_version and \
            parameters and client_token and \
            mode and target_account and \
            targets and target_maps and \
            max_concurrency and max_errors and \
            target_locations and tags and alarm_configuration):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            document_name = req_body.get('DocumentName')
            document_version = req_body.get('DocumentVersion')
            parameters = req_body.get('Parameters')
            client_token = req_body.get('ClientToken')
            mode = req_body.get('Mode')
            target_account = req_body.get('TargetAccount')
            targets = req_body.get('Targets')
            target_maps = req_body.get('TargetMaps')
            max_concurrency = req_body.get('MaxConcurrency')
            max_errors = req_body.get('MaxErrors')
            target_locations = req_body.get('TargetLocations')
            tags = req_body.get('Tags')
            alarm_configuration = req_body.get('AlarmConfiguration')

    # Set parameter dictionary based on the provided request parameters
    kwargs = {}
    if document_name:
        kwargs['DocumentName'] = document_name
    if document_version:
        kwargs['DocumentVersion'] = document_version
    if parameters:
        kwargs['Parameters'] = parameters
    if client_token:
        kwargs['ClientToken'] = client_token
    if mode:
        kwargs['Mode'] = mode
    if target_account:
        kwargs['TargetAccount'] = target_account
    if targets:
        kwargs['Targets'] = targets
    if target_maps:
        kwargs['TargetMaps'] = target_maps
    if max_concurrency:
        kwargs['MaxConcurrency'] = max_concurrency
    if max_errors:
        kwargs['MaxErrors'] = max_errors
    if target_locations:
        kwargs['TargetLocations'] = target_locations
    if tags:
        kwargs['Tags'] = tags
    if alarm_configuration:
        kwargs['AlarmConfiguration'] = alarm_configuration

    if document_name:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function to start atuomation execution.')

                results = ssm_client.start_automation_execution(**kwargs)
                
                logging.info('Call to start automation execution successful.')

                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
            
            except ssm_client.exceptions.InternalServerError as ex:
                logging.error(f"Internal Server Exception: {str(ex)}")
                return func.HttpResponse("Internal Server Exception", status_code=500)

            except ssm_client.exceptions.AutomationDefinitionNotFoundException as ex:
                logging.error(f"Automation Definition Not Found Exception: {str(ex)}")
                return func.HttpResponse("Automation Definition Not Found Exception", status_code=400)

            except ssm_client.exceptions.InvalidAutomationExecutionParametersException as ex:
                logging.error(f"Invalid Automation Execution Parameters Exception: {str(ex)}")
                return func.HttpResponse("Invalid Automation Execution Parameters Exception", status_code=400)
            
            except ssm_client.exceptions.AutomationExecutionLimitExceededException as ex:
                logging.error(f"Automation Execution Limit Exceeded Exception: {str(ex)}")
                return func.HttpResponse("Automation Execution Limit Exceeded Exception", status_code=400)
            
            except ssm_client.exceptions.AutomationDefinitionVersionNotFoundException as ex:
                logging.error(f"Automation Definition Version Not Found Exception: {str(ex)}")
                return func.HttpResponse("Automation Definition Version Not Found Exception", status_code=400)
            
            except ssm_client.exceptions.IdempotentParameterMismatch as ex:
                logging.error(f"Idempotent Parameter Mismatch: {str(ex)}")
                return func.HttpResponse("Idempotent Parameter Mismatch", status_code=400)
            
            except ssm_client.exceptions.InvalidTarget as ex:
                logging.error(f"Invalid Target: {str(ex)}")
                return func.HttpResponse("Invalid Target", status_code=400)
        
        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass DocumentName, other optional parameters in the query string or request body.",
             status_code=400
        )
