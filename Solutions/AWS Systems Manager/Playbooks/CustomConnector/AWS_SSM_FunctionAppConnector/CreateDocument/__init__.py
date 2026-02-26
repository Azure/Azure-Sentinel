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

    # Get Content, Requires, Attachments, Name, DisplayName, VersionName, DocumentType, DocumentFormat, TargetType and Tags from the request parameters
    content = req.params.get('Content')
    requires = req.params.get('Requires')
    attachments = req.params.get('Attachments')
    name = req.params.get('Name')
    display_name = req.params.get('DisplayName')
    version_name = req.params.get('VersionName')
    document_type = req.params.get('DocumentType')
    document_format = req.params.get('DocumentFormat')
    target_type = req.params.get('TargetType')
    tags = req.params.get('Tags')

    if not (content or requires or attachments or name or display_name or version_name or document_type or document_format or target_type or tags):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            content = req_body.get('Content')
            requires = req_body.get('Requires')
            attachments = req_body.get('Attachments')
            name = req_body.get('Name')
            display_name = req_body.get('DisplayName')
            version_name = req_body.get('VersionName')
            document_type = req_body.get('DocumentType')
            document_format = req_body.get('DocumentFormat')
            target_type = req_body.get('TargetType')
            tags = req_body.get('Tags')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if content:
        kwargs['Content'] = content
    if requires:
        kwargs['Requires'] = requires
    if attachments:
        kwargs['Attachments'] = attachments
    if name:
        kwargs['Name'] = name
    if display_name:
        kwargs['DisplayName'] = display_name
    if version_name:
        kwargs['VersionName'] = version_name
    if document_type:
        kwargs['DocumentType'] = document_type
    if document_format:
        kwargs['DocumentFormat'] = document_format
    if target_type:
        kwargs['TargetType'] = target_type
    if tags:
        kwargs['Tags'] = tags

    if content and name:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function to create AWS SSM Document.')

                results = ssm_client.create_document(**kwargs)
                print(results)
                logging.info('Call to create AWS SSM Document successful.')

                # Result returns CreatedDate as datetime object. Convert datetime to string
                if results:
                    if ('DocumentDescription' in results) and ('CreatedDate' in results['DocumentDescription']):
                        results['DocumentDescription']['CreatedDate'] = results['DocumentDescription']['CreatedDate'].strftime("%Y-%m-%dT%H:%M:%S%z")
                    if ('DocumentDescription' in results) and ('ReviewInformation' in results['DocumentDescription']):
                        for review in results['DocumentDescription']['ReviewInformation']:
                            if results['DocumentDescription']['ReviewInformation'][review] and results['DocumentDescription']['ReviewInformation'][review]['ReviewedTime']:
                                results['DocumentDescription']['ReviewInformation'][review]['ReviewedTime'] = results['DocumentDescription']['ReviewInformation'][review]['ReviewedTime'].strftime("%Y-%m-%dT%H:%M:%S%z")
                

                logging.info('Datetime object converted to string.')

                # Return the results
                return func.HttpResponse(
                    json.dumps(results),
                    headers = {"Content-Type": "application/json"},
                    status_code = 200
                )
            
            except ssm_client.exceptions.InternalServerError as ex:
                logging.error(f"Internal Server Exception: {str(ex)}")
                return func.HttpResponse("Internal Server Exception", status_code=500)

            except ssm_client.exceptions.DocumentAlreadyExists as ex:
                logging.error(f"Document Already Exists Exception: {str(ex)}")
                return func.HttpResponse("Document Already Exists Exception", status_code=400)

            except ssm_client.exceptions.MaxDocumentSizeExceeded as ex:
                logging.error(f"Max Document Size Exceeded Exception: {str(ex)}")
                return func.HttpResponse("Max Document Size Exceeded Exception", status_code=400)
            
            except ssm_client.exceptions.InvalidDocumentContent as ex:
                logging.error(f"Invalid Document Content: {str(ex)}")
                return func.HttpResponse("Invalid Document Content", status_code=400)
            
            except ssm_client.exceptions.DocumentLimitExceeded as ex:
                logging.error(f"Document Limit Exceeded: {str(ex)}")
                return func.HttpResponse("Document Limit Exceeded", status_code=400)
            
            except ssm_client.exceptions.InvalidDocumentSchemaVersion as ex:
                logging.error(f"Invalid Document SchemaVersion: {str(ex)}")
                return func.HttpResponse("Invalid Document SchemaVersion", status_code=400)
            
        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass Content and Name parameters in the query string or request body.",
             status_code=400
        )
