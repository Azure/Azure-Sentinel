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

    # Get Name, VersionName and DocumentVersion from the request parameters
    name = req.params.get('Name')
    version_name = req.params.get('VersionName')
    document_version = req.params.get('DocumentVersion')

    if not (name and version_name and document_version):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('Name')
            version_name = req_body.get('VersionName')
            document_version = req_body.get('DocumentVersion')
    
    # Set parameter dictionary based on the request parameters
    kwargs = {}
    if name:
        kwargs['Name'] = name
    if version_name:
        kwargs['VersionName'] = version_name
    if document_version:
        kwargs['DocumentVersion'] = document_version

    if name:
        try:
            logging.info('Creating Boto3 SSM Client.')
            ssm_client = boto3.client(
                "ssm",
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id, 
                aws_secret_access_key=aws_secret_access_key
            )

            try:
                logging.info('Calling function to get AWS SSM Document.')

                results = ssm_client.get_document(**kwargs)

                logging.info('Call to get AWS SSM Document successful.')

                # Result returns CreatedDate as datetime object. Convert datetime to string
                if results and ('CreatedDate' in results) and (results['CreatedDate'] != ''):
                    results['CreatedDate'] = results['CreatedDate'].strftime("%Y-%m-%dT%H:%M:%S%z")

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

            except ssm_client.exceptions.InvalidDocument as ex:
                logging.error(f"Invalid Document Exception: {str(ex)}")
                return func.HttpResponse("Invalid Document Exception", status_code=400)

            except ssm_client.exceptions.InvalidDocumentVersion as ex:
                logging.error(f"Invalid Document Version Exception: {str(ex)}")
                return func.HttpResponse("Invalid Document Version Exception", status_code=400)
            
        except ClientError as ex:
            logging.error(f"SSM Client Error: {str(ex)}")
            return func.HttpResponse("SSM Client Error", status_code=401)
        
        except Exception as ex:
            logging.error(f"Exception Occured: {str(ex)}")
            return func.HttpResponse("Internal Server Exception", status_code=500)
        
    else:
        return func.HttpResponse(
             "Pass Name (required) and (optional) VersionName and DocumentVersion parameter(s) in the query string or request body.",
             status_code=400
        )
